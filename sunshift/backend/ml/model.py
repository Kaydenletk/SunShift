from __future__ import annotations

import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from backend.ml.features import FeatureEngineer

# Suppress Prophet's verbose logging
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


class SunShiftModel:
    """Prophet + XGBoost ensemble model for electricity cost prediction.

    Prophet provides a demand time-series baseline which is fed as an
    additional feature into XGBoost for final cost prediction.
    """

    def __init__(self) -> None:
        self.prophet_model: Prophet | None = None
        self.xgb_model: XGBRegressor | None = None
        self.feature_engineer = FeatureEngineer()
        self.metrics: dict = {}

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, data: pd.DataFrame, test_ratio: float = 0.2) -> dict:
        """Train the ensemble on historical data.

        Args:
            data: DataFrame with columns timestamp, temperature_f, humidity,
                  demand_mw, cost_cents_kwh.
            test_ratio: Fraction of data (tail) used as hold-out test set.

        Returns:
            dict with keys: mape, mae, train_size, test_size.
        """
        data = self.feature_engineer.build_features(data)
        data = data.reset_index(drop=True)
        split_idx = int(len(data) * (1 - test_ratio))
        train_df = data.iloc[:split_idx].copy()

        # --- Prophet: train on demand time-series ---
        prophet_df = train_df[["timestamp", "demand_mw"]].rename(
            columns={"timestamp": "ds", "demand_mw": "y"}
        )
        # Prophet requires timezone-naive datetimes
        prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)

        self.prophet_model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
        )
        self.prophet_model.fit(prophet_df)

        # --- Add Prophet predictions as a feature for XGBoost ---
        all_prophet_df = data[["timestamp"]].rename(columns={"timestamp": "ds"}).copy()
        all_prophet_df["ds"] = all_prophet_df["ds"].dt.tz_localize(None)
        prophet_forecast = self.prophet_model.predict(all_prophet_df)
        data = data.copy()
        data["prophet_demand"] = prophet_forecast["yhat"].values

        # Rebuild train/test splits with prophet feature
        train_df = data.iloc[:split_idx]
        test_df = data.iloc[split_idx:]

        feature_cols = self.feature_engineer.get_feature_columns() + ["prophet_demand"]
        X_train = train_df[feature_cols].values
        y_train = train_df["cost_cents_kwh"].values
        X_test = test_df[feature_cols].values
        y_test = test_df["cost_cents_kwh"].values

        # --- XGBoost ---
        self.xgb_model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        self.xgb_model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        # --- Evaluate on hold-out set ---
        y_pred = self.xgb_model.predict(X_test)
        self.metrics = {
            "mape": float(mean_absolute_percentage_error(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "test_size": int(len(y_test)),
            "train_size": int(len(y_train)),
        }
        return self.metrics

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict cost_cents_kwh for each row in data.

        Args:
            data: DataFrame with columns timestamp, temperature_f, humidity,
                  demand_mw (cost_cents_kwh not required at inference time).

        Returns:
            numpy array of predicted cost values (clipped to >= 0).
        """
        if self.xgb_model is None or self.prophet_model is None:
            raise RuntimeError("Model not trained. Call train() or load() first.")

        data = self.feature_engineer.build_features(data)
        data = data.reset_index(drop=True)

        prophet_df = data[["timestamp"]].rename(columns={"timestamp": "ds"}).copy()
        prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)
        prophet_forecast = self.prophet_model.predict(prophet_df)
        data = data.copy()
        data["prophet_demand"] = prophet_forecast["yhat"].values

        feature_cols = self.feature_engineer.get_feature_columns() + ["prophet_demand"]
        X = data[feature_cols].values
        predictions = self.xgb_model.predict(X)
        return np.maximum(predictions, 0)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        """Serialize models to disk.

        - XGBoost: joblib
        - Prophet: JSON (via prophet.serialize)
        - Metrics: JSON
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.xgb_model, path / "xgb_model.joblib")

        with open(path / "prophet_model.json", "w") as f:
            f.write(model_to_json(self.prophet_model))

        with open(path / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> SunShiftModel:
        """Deserialize models from disk."""
        path = Path(path)
        instance = cls()

        instance.xgb_model = joblib.load(path / "xgb_model.joblib")

        with open(path / "prophet_model.json", "r") as f:
            instance.prophet_model = model_from_json(f.read())

        if (path / "metrics.json").exists():
            with open(path / "metrics.json") as f:
                instance.metrics = json.load(f)

        return instance
