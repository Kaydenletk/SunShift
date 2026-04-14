"""ML prediction mock data."""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PredictionData:
    """Price prediction data."""
    timestamp: datetime
    predicted_rate: float
    confidence: float
    is_optimal_window: bool


def get_predictions(hours: int = 24) -> list[PredictionData]:
    """Get mock ML predictions for next N hours."""
    now = datetime.now()
    predictions = []

    for i in range(hours):
        future_time = now + timedelta(hours=i)
        hour = future_time.hour

        is_peak = 12 <= hour < 21
        base_rate = 0.18 if is_peak else 0.04
        variance = 0.01 if is_peak else 0.005
        predicted_rate = base_rate + (i % 3 - 1) * variance
        confidence = max(0.75, 0.98 - (i * 0.01))
        is_optimal = not is_peak and confidence > 0.85

        predictions.append(PredictionData(
            timestamp=future_time,
            predicted_rate=predicted_rate,
            confidence=confidence,
            is_optimal_window=is_optimal,
        ))

    return predictions


def get_prediction_accuracy() -> dict:
    """Get mock prediction accuracy metrics."""
    return {
        "mae": 0.012,
        "rmse": 0.018,
        "mape": 8.5,
        "accuracy_percent": 91.5,
    }


def get_weekly_summary() -> list[dict]:
    """Get mock weekly cost summary."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [
        {"name": day, "local": 85 + i * 5, "cloud": 35 + i * 2}
        for i, day in enumerate(days)
    ]
