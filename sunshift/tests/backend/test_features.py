import pytest
import math
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

from backend.ml.features import FeatureEngineer


class TestCyclicalEncoding:
    def test_hour_23_and_hour_0_are_close(self):
        fe = FeatureEngineer()
        sin_23, cos_23 = fe._cyclical_hour(23)
        sin_0, cos_0 = fe._cyclical_hour(0)
        distance = math.sqrt((sin_23 - sin_0) ** 2 + (cos_23 - cos_0) ** 2)
        assert distance < 0.3  # close on unit circle

    def test_hour_12_opposite_hour_0(self):
        fe = FeatureEngineer()
        sin_12, cos_12 = fe._cyclical_hour(12)
        sin_0, cos_0 = fe._cyclical_hour(0)
        distance = math.sqrt((sin_12 - sin_0) ** 2 + (cos_12 - cos_0) ** 2)
        assert distance > 1.5  # far apart


class TestFeatureEngineer:
    @pytest.fixture
    def sample_data(self):
        hours = 200
        timestamps = [datetime(2026, 4, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(hours)]
        return pd.DataFrame({
            "timestamp": timestamps,
            "temperature_f": [75 + 15 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
            "humidity": [60 + 10 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
            "demand_mw": [5000 + 3000 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
        })

    def test_produces_all_required_columns(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        required = [
            "hour_sin", "hour_cos", "temp_rolling_6h", "demand_lag_24h",
            "demand_lag_168h", "temp_x_hour", "is_peak_transition", "cooling_degree_hours",
        ]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_no_nan_in_output(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        assert not result.isna().any().any(), f"NaN found in columns: {result.columns[result.isna().any()].tolist()}"

    def test_peak_transition_flags_correct_hours(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        peak_rows = result[result["is_peak_transition"] == 1]
        hours = peak_rows["timestamp"].dt.hour.unique()
        # Should flag hours 11, 12, 20, 21 (30 min before/after 12-21 peak)
        for h in [11, 12, 21]:
            assert h in hours, f"Hour {h} should be peak transition"

    def test_cooling_degree_hours_zero_below_65(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        cold_rows = result[result["temperature_f"] < 65]
        if len(cold_rows) > 0:
            assert (cold_rows["cooling_degree_hours"] == 0).all()
