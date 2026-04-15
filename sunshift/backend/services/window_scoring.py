"""Window scoring service for AI Scheduler.

This module implements the probabilistic window scoring formula:
    score = (peak_cost - window_cost) * confidence^2 * duration_hours

The confidence squared term penalizes uncertain forecasts quadratically,
preferring reliable windows over potentially better but uncertain ones.
This reflects the real-world risk that a low-confidence forecast might
be significantly wrong, making the actual savings unpredictable.

Example:
    A window with 90% confidence retains 81% of its score (0.9^2),
    while a window with 60% confidence only retains 36% (0.6^2).
    This means a high-confidence window needs to be only 2.25x better
    than a low-confidence window to be preferred, rather than having
    to be absolutely better.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.scheduler import CostWindow

# Conversion constant
CENTS_PER_DOLLAR = 100


@dataclass
class ScoredWindow:
    """A cost window with computed score and ranking.

    Attributes:
        window: The original CostWindow being scored.
        score: Computed score using probabilistic formula (higher is better).
        rank: Ranking position (1 = best), assigned by rank_windows().
        estimated_savings_dollars: Estimated dollar savings for this window.
    """

    window: CostWindow
    score: float
    rank: int = 0
    estimated_savings_dollars: float = 0.0


class WindowScorer:
    """Scores and ranks cost windows for optimal workload scheduling.

    The scoring formula balances three factors:
    1. Cost savings: Higher savings from peak price = higher score
    2. Confidence: Uncertain forecasts are penalized quadratically
    3. Duration: Longer windows offer more scheduling flexibility

    The confidence squared term is the key innovation - it models the
    risk that low-confidence forecasts might be significantly wrong,
    making the expected value of uncertain windows lower than their
    nominal savings would suggest.

    Attributes:
        peak_cost_cents: Reference peak electricity cost in cents/kWh.
        kwh_per_hour: Estimated workload power consumption for savings calc.

    Example:
        >>> scorer = WindowScorer(peak_cost_cents=25.0)
        >>> window = CostWindow(start=..., end=..., avg_cost_cents_kwh=8.0, confidence=0.85)
        >>> scored = scorer.score_window(window)
        >>> print(f"Score: {scored.score}, Savings: ${scored.estimated_savings_dollars}")
    """

    def __init__(
        self,
        peak_cost_cents: float = 25.0,
        kwh_per_hour: float = 2.5,
    ) -> None:
        """Initialize the scorer with reference peak cost.

        Args:
            peak_cost_cents: Reference peak electricity cost in cents/kWh.
                Default 25.0 reflects FPL TOU peak pricing.
            kwh_per_hour: Estimated workload power consumption in kWh/hour.
                Used for dollar savings estimation. Default 2.5 represents
                typical SMB server workload.
        """
        self.peak_cost_cents = peak_cost_cents
        self.kwh_per_hour = kwh_per_hour

    def score_window(self, window: CostWindow) -> ScoredWindow:
        """Score a single cost window using the probabilistic formula.

        Formula: score = (peak_cost - window_cost) * confidence^2 * duration_hours

        Args:
            window: The CostWindow to score.

        Returns:
            ScoredWindow containing the original window, computed score,
            and estimated dollar savings.

        Note:
            Negative scores are possible if window cost exceeds peak cost.
            Estimated savings are clamped to 0 (no negative savings reported).
        """
        duration_hours = (window.end - window.start).total_seconds() / 3600
        savings_per_hour = self.peak_cost_cents - window.avg_cost_cents_kwh
        confidence_factor = window.confidence ** 2

        score = savings_per_hour * confidence_factor * duration_hours

        # Estimate dollar savings (only if positive)
        estimated_kwh = self.kwh_per_hour * duration_hours
        savings_dollars = (savings_per_hour / CENTS_PER_DOLLAR) * estimated_kwh

        return ScoredWindow(
            window=window,
            score=round(score, 2),
            estimated_savings_dollars=round(max(0, savings_dollars), 2),
        )

    def rank_windows(
        self,
        windows: list[CostWindow],
        top_n: int = 3,
    ) -> list[ScoredWindow]:
        """Score and rank multiple windows, returning the top N.

        Args:
            windows: List of CostWindows to score and rank.
            top_n: Number of top windows to return.

        Returns:
            List of top_n ScoredWindows, sorted by score descending,
            with rank assigned (1 = best).
        """
        scored = [self.score_window(w) for w in windows]
        scored.sort(key=lambda sw: sw.score, reverse=True)

        # Return new instances with rank assigned (immutable pattern)
        return [
            ScoredWindow(
                window=sw.window,
                score=sw.score,
                rank=rank,
                estimated_savings_dollars=sw.estimated_savings_dollars,
            )
            for rank, sw in enumerate(scored[:top_n], 1)
        ]
