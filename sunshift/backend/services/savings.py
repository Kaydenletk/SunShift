"""Savings calculation service — placeholder for SP2."""
from __future__ import annotations

from backend.models.prediction import PredictionResponse


def estimate_savings(prediction: PredictionResponse, workload_hours: int = 4) -> float:
    """
    Rough savings estimate: cost of running during peak vs. optimal window.

    Returns estimated savings in dollars.
    """
    if not prediction.hourly_forecast or not prediction.optimal_windows:
        return 0.0

    peak_cost = max(f.cost_cents_kwh for f in prediction.hourly_forecast)
    best_window = prediction.optimal_windows[0]
    savings_per_kwh_cents = peak_cost - best_window.avg_cost_cents_kwh

    # Assume a modest 500W average draw per compute hour
    kwh_per_hour = 0.5
    total_kwh = kwh_per_hour * workload_hours
    savings_cents = savings_per_kwh_cents * total_kwh
    return round(savings_cents / 100, 4)
