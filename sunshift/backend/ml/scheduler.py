from __future__ import annotations

from datetime import datetime, timedelta
from backend.models.prediction import OptimalWindow


def find_cheapest_windows(
    timestamps: list[datetime],
    costs: list[float],
    min_duration: int = 2,
    max_duration: int = 8,
    top_n: int = 3,
) -> list[OptimalWindow]:
    if len(timestamps) != len(costs):
        raise ValueError("timestamps and costs must have same length")

    candidates: list[OptimalWindow] = []

    for duration in range(min_duration, max_duration + 1):
        for i in range(len(costs) - duration + 1):
            window_costs = costs[i : i + duration]
            avg_cost = sum(window_costs) / len(window_costs)
            peak_avg = 25.0  # approximate peak cost for savings calc
            savings = (peak_avg - avg_cost) * duration * 2.5 / 100  # rough kWh * hours

            candidates.append(OptimalWindow(
                rank=0,
                start=timestamps[i],
                end=timestamps[i] + timedelta(hours=duration),
                avg_cost_cents_kwh=round(avg_cost, 2),
                estimated_savings_dollars=round(max(0, savings), 2),
                workload_recommendation="FULL_SYNC" if duration >= 4 else "INCREMENTAL_SYNC",
            ))

    candidates.sort(key=lambda w: w.avg_cost_cents_kwh)
    top = candidates[:top_n]
    for rank, window in enumerate(top, 1):
        window.rank = rank
    return top
