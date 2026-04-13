import pytest
import numpy as np
from datetime import datetime, timezone, timedelta

from backend.ml.scheduler import find_cheapest_windows
from backend.ml.predict import PredictionService, FallbackPrediction


class TestFindCheapestWindows:
    def test_finds_cheapest_consecutive_hours(self):
        costs = [20, 22, 25, 27, 26, 24, 18, 12, 8, 6, 5, 6, 8, 10, 14, 18, 20, 22, 25, 27, 26, 22, 15, 10]
        base = datetime(2026, 4, 13, tzinfo=timezone.utc)
        timestamps = [base + timedelta(hours=i) for i in range(24)]
        windows = find_cheapest_windows(timestamps, costs, min_duration=3, max_duration=6, top_n=2)
        assert len(windows) == 2
        assert windows[0].avg_cost_cents_kwh < windows[1].avg_cost_cents_kwh
        # Cheapest 3h window should be around hours 8-10 (costs 6, 5, 6)
        assert windows[0].start.hour in range(8, 12)

    def test_respects_min_duration(self):
        costs = [10] * 24
        base = datetime(2026, 4, 13, tzinfo=timezone.utc)
        timestamps = [base + timedelta(hours=i) for i in range(24)]
        windows = find_cheapest_windows(timestamps, costs, min_duration=4, max_duration=8, top_n=1)
        assert len(windows) == 1
        duration_hours = (windows[0].end - windows[0].start).total_seconds() / 3600
        assert duration_hours >= 4


class TestFallbackPrediction:
    def test_fallback_returns_static_peak(self):
        fb = FallbackPrediction(peak_start=12, peak_end=21)
        forecast = fb.generate(datetime(2026, 4, 13, tzinfo=timezone.utc))
        assert len(forecast) == 48
        peak_cost = next(f for f in forecast if f.hour.hour == 14).cost_cents_kwh
        offpeak_cost = next(f for f in forecast if f.hour.hour == 3).cost_cents_kwh
        assert peak_cost > offpeak_cost
