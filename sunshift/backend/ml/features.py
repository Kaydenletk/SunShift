from __future__ import annotations

import math
import pandas as pd
import numpy as np


class FeatureEngineer:
    PEAK_START = 12  # FPL TOU peak start
    PEAK_END = 21    # FPL TOU peak end

    def _cyclical_hour(self, hour: int) -> tuple[float, float]:
        sin_val = math.sin(2 * math.pi * hour / 24)
        cos_val = math.cos(2 * math.pi * hour / 24)
        return sin_val, cos_val

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        hour = df["timestamp"].dt.hour

        # Cyclical encoding
        df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
        df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

        # Rolling temperature (6h window)
        df["temp_rolling_6h"] = df["temperature_f"].rolling(window=6, min_periods=1).mean()

        # Lag features — fill missing history with 0 (insufficient data)
        df["demand_lag_24h"] = df["demand_mw"].shift(24).fillna(0)
        df["demand_lag_168h"] = df["demand_mw"].shift(168).fillna(0)

        # Flag rows where lag values were filled due to insufficient history
        df["demand_lag_24h_missing"] = (df["demand_mw"].shift(24).isna()).astype(int)
        df["demand_lag_168h_missing"] = (df["demand_mw"].shift(168).isna()).astype(int)

        # Interaction: temperature * hour_sin (captures temp-at-time-of-day effect)
        # e.g. 95°F at 2PM causes AC spike; 95°F at 2AM doesn't
        df["temp_x_hour"] = df["temperature_f"] * df["hour_sin"]

        # Peak transition flag: within 1 hour of peak boundaries (hours 11, 12, 20, 21)
        df["is_peak_transition"] = (
            ((hour >= self.PEAK_START - 1) & (hour <= self.PEAK_START)) |
            ((hour >= self.PEAK_END) & (hour <= self.PEAK_END + 1))
        ).astype(int)

        # Cooling degree hours: degrees above 65°F baseline (0 when below 65)
        df["cooling_degree_hours"] = np.maximum(0, df["temperature_f"] - 65)

        # Day of week (0=Monday, 6=Sunday)
        df["day_of_week"] = df["timestamp"].dt.dayofweek

        # Is weekend
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        # Month
        df["month"] = df["timestamp"].dt.month

        # Is FPL peak period
        df["is_fpl_peak"] = ((hour >= self.PEAK_START) & (hour < self.PEAK_END)).astype(int)

        return df

    def get_feature_columns(self) -> list[str]:
        """Return the list of feature columns suitable for XGBoost input."""
        return [
            "hour_sin", "hour_cos", "temp_rolling_6h", "demand_lag_24h",
            "demand_lag_168h", "temp_x_hour", "is_peak_transition",
            "cooling_degree_hours", "day_of_week", "is_weekend", "month",
            "is_fpl_peak", "temperature_f", "humidity",
        ]
