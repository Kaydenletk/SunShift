"""FPL TOU pricing mock data."""

from dataclasses import dataclass
from datetime import time


@dataclass
class PricingData:
    """Electricity pricing data."""
    current_rate: float
    off_peak_rate: float
    is_peak: bool
    peak_start: time
    peak_end: time
    multiplier: float


def get_pricing_data(current_hour: int = 14) -> PricingData:
    """Get mock FPL TOU pricing data."""
    is_peak = 12 <= current_hour < 21

    return PricingData(
        current_rate=0.18 if is_peak else 0.04,
        off_peak_rate=0.04,
        is_peak=is_peak,
        peak_start=time(12, 0),
        peak_end=time(21, 0),
        multiplier=4.5,
    )


def get_hourly_rates(hours: int = 24) -> list[dict]:
    """Get hourly rate forecast."""
    rates = []
    for hour in range(hours):
        is_peak = 12 <= hour < 21
        rates.append({
            "hour": hour,
            "rate": 0.18 if is_peak else 0.04,
            "is_peak": is_peak,
        })
    return rates
