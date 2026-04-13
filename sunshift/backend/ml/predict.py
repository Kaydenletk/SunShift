from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from backend.models.prediction import HourlyForecast, PredictionResponse
from backend.ml.model import SunShiftModel
from backend.ml.scheduler import find_cheapest_windows
from backend.core.config import settings


class FallbackPrediction:
    def __init__(self, peak_start: int = 12, peak_end: int = 21):
        self.peak_start = peak_start
        self.peak_end = peak_end

    def generate(self, start: datetime) -> list[HourlyForecast]:
        forecasts = []
        for i in range(48):
            hour_dt = start + timedelta(hours=i)
            h = hour_dt.hour
            if self.peak_start <= h < self.peak_end:
                cost = 25.0
                demand = 8500.0
            else:
                cost = 7.0
                demand = 4500.0
            forecasts.append(HourlyForecast(
                hour=hour_dt, cost_cents_kwh=cost, demand_mw=demand, confidence=0.3,
            ))
        return forecasts


class PredictionService:
    def __init__(self, model_path: Path | None = None):
        self.model: SunShiftModel | None = None
        self.fallback = FallbackPrediction(settings.fallback_peak_start_hour, settings.fallback_peak_end_hour)
        self._cache: dict[str, tuple[float, PredictionResponse]] = {}
        self._cache_ttl = settings.prediction_cache_ttl_seconds

        if model_path and model_path.exists():
            self.model = SunShiftModel.load(model_path)

    def predict(self, location: str = "tampa_fl") -> PredictionResponse:
        # Check cache
        cache_key = f"{location}:{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H')}"
        if cache_key in self._cache:
            cached_time, cached_response = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_response

        now = datetime.now(timezone.utc)

        # Circuit breaker: use fallback if no model
        if self.model is None:
            forecasts = self.fallback.generate(now)
        else:
            try:
                forecasts = self._run_model(now)
            except Exception:
                forecasts = self.fallback.generate(now)

        timestamps = [f.hour for f in forecasts]
        costs = [f.cost_cents_kwh for f in forecasts]
        windows = find_cheapest_windows(timestamps, costs, min_duration=2, max_duration=8)

        response = PredictionResponse(
            prediction_id=f"pred_{now.strftime('%Y%m%d_%H%M')}",
            location=location,
            generated_at=now,
            model_version=settings.model_version,
            hourly_forecast=forecasts,
            optimal_windows=windows,
            explanation=self._generate_explanation(forecasts, windows),
        )

        self._cache[cache_key] = (time.time(), response)
        return response

    def _run_model(self, start: datetime) -> list[HourlyForecast]:
        # In production, this would fetch real data and run the model.
        # For now, use fallback as placeholder until real data pipeline is connected.
        return self.fallback.generate(start)

    def _generate_explanation(self, forecasts: list[HourlyForecast], windows) -> str:
        if not windows:
            return "No optimal windows found."
        peak = max(forecasts, key=lambda f: f.cost_cents_kwh)
        best = windows[0]
        return (
            f"Electricity costs peak at {peak.hour.strftime('%I%p')} "
            f"({peak.cost_cents_kwh:.1f}¢/kWh). "
            f"Best window: {best.start.strftime('%I%p')}-{best.end.strftime('%I%p')} "
            f"at {best.avg_cost_cents_kwh:.1f}¢/kWh average "
            f"— {((peak.cost_cents_kwh - best.avg_cost_cents_kwh) / peak.cost_cents_kwh * 100):.0f}% cheaper."
        )
