"""Tests for window scoring service.

This module tests the WindowScorer class which implements the probabilistic
scoring formula: score = (peak_cost - window_cost) × confidence² × duration_hours

The confidence² term penalizes uncertain forecasts quadratically, preferring
reliable windows over potentially better but uncertain ones.
"""

from datetime import datetime, timedelta, timezone

import pytest

from backend.models.scheduler import CostWindow, RiskLevel
from backend.services.window_scoring import ScoredWindow, WindowScorer


class TestWindowScorer:
    """Tests for WindowScorer scoring and ranking logic."""

    @pytest.fixture
    def scorer(self) -> WindowScorer:
        """Create a WindowScorer with default peak cost."""
        return WindowScorer(peak_cost_cents=25.0)

    def test_score_formula_correct(self, scorer: WindowScorer) -> None:
        """Verify: score = (peak - window) × conf² × hours"""
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer.score_window(window)
        # (25 - 8) × 0.85² × 4 = 17 × 0.7225 × 4 = 49.13
        assert abs(scored.score - 49.13) < 0.1

    def test_low_confidence_reduces_score(self, scorer: WindowScorer) -> None:
        """Low confidence should significantly reduce score due to confidence²."""
        now = datetime.now(timezone.utc)
        high_conf = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.90,
            weather_risk=RiskLevel.LOW,
        )
        low_conf = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.60,
            weather_risk=RiskLevel.LOW,
        )
        high_scored = scorer.score_window(high_conf)
        low_scored = scorer.score_window(low_conf)
        # 0.90² / 0.60² = 0.81 / 0.36 = 2.25x difference
        assert high_scored.score > low_scored.score * 2

    def test_longer_window_higher_score(self, scorer: WindowScorer) -> None:
        """Same cost, longer duration = higher score."""
        now = datetime.now(timezone.utc)
        short = CostWindow(
            start=now,
            end=now + timedelta(hours=2),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        long = CostWindow(
            start=now,
            end=now + timedelta(hours=6),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        short_scored = scorer.score_window(short)
        long_scored = scorer.score_window(long)
        assert long_scored.score > short_scored.score

    def test_ranks_windows_correctly(self, scorer: WindowScorer) -> None:
        """Best score gets rank 1."""
        now = datetime.now(timezone.utc)
        windows = [
            CostWindow(
                start=now,
                end=now + timedelta(hours=4),
                avg_cost_cents_kwh=15.0,
                confidence=0.80,
                weather_risk=RiskLevel.LOW,
            ),
            CostWindow(
                start=now + timedelta(hours=4),
                end=now + timedelta(hours=8),
                avg_cost_cents_kwh=8.0,
                confidence=0.90,
                weather_risk=RiskLevel.LOW,
            ),
            CostWindow(
                start=now + timedelta(hours=8),
                end=now + timedelta(hours=12),
                avg_cost_cents_kwh=10.0,
                confidence=0.85,
                weather_risk=RiskLevel.LOW,
            ),
        ]
        ranked = scorer.rank_windows(windows, top_n=3)
        assert ranked[0].rank == 1
        assert ranked[0].score > ranked[1].score
        assert ranked[1].score > ranked[2].score

    def test_negative_savings_handled(self, scorer: WindowScorer) -> None:
        """Windows with higher cost than peak should still be scored (negative score)."""
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now + timedelta(hours=2),
            avg_cost_cents_kwh=30.0,  # Higher than peak (25)
            confidence=0.90,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer.score_window(window)
        # (25 - 30) × 0.9² × 2 = -5 × 0.81 × 2 = -8.1
        assert scored.score < 0
        assert scored.estimated_savings_dollars == 0  # No negative savings

    def test_zero_duration_window(self, scorer: WindowScorer) -> None:
        """Zero duration window should have zero score."""
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now,  # Same start and end
            avg_cost_cents_kwh=8.0,
            confidence=0.90,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer.score_window(window)
        assert scored.score == 0

    def test_estimated_savings_calculation(self, scorer: WindowScorer) -> None:
        """Estimated savings should be calculated correctly."""
        scorer_with_kwh = WindowScorer(peak_cost_cents=25.0, kwh_per_hour=2.5)
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.90,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer_with_kwh.score_window(window)
        # Savings per kWh = (25 - 8) / 100 = $0.17
        # Total kWh = 2.5 * 4 = 10
        # Estimated savings = 0.17 * 10 = $1.70
        assert abs(scored.estimated_savings_dollars - 1.70) < 0.01

    def test_rank_windows_top_n(self, scorer: WindowScorer) -> None:
        """rank_windows should return only top_n windows."""
        now = datetime.now(timezone.utc)
        windows = [
            CostWindow(
                start=now + timedelta(hours=i),
                end=now + timedelta(hours=i + 2),
                avg_cost_cents_kwh=float(10 + i),
                confidence=0.85,
                weather_risk=RiskLevel.LOW,
            )
            for i in range(5)
        ]
        ranked = scorer.rank_windows(windows, top_n=2)
        assert len(ranked) == 2
        assert ranked[0].rank == 1
        assert ranked[1].rank == 2

    def test_rank_windows_assigns_sequential_ranks(self, scorer: WindowScorer) -> None:
        """Ranks should be assigned sequentially starting from 1."""
        now = datetime.now(timezone.utc)
        windows = [
            CostWindow(
                start=now + timedelta(hours=i * 4),
                end=now + timedelta(hours=(i + 1) * 4),
                avg_cost_cents_kwh=float(8 + i * 2),
                confidence=0.85,
                weather_risk=RiskLevel.LOW,
            )
            for i in range(4)
        ]
        ranked = scorer.rank_windows(windows, top_n=4)
        assert [w.rank for w in ranked] == [1, 2, 3, 4]

    def test_scored_window_contains_original_window(self, scorer: WindowScorer) -> None:
        """ScoredWindow should contain reference to original CostWindow."""
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer.score_window(window)
        assert scored.window == window
        assert scored.window.avg_cost_cents_kwh == 8.0
