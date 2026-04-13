import pytest
import math
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path

from backend.ml.model import SunShiftModel


def _synthetic_training_data(days: int = 90) -> pd.DataFrame:
    hours = days * 24
    timestamps = [datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(hours)]
    hour_vals = [t.hour for t in timestamps]
    rng = np.random.default_rng(42)
    rows = []
    for i, ts in enumerate(timestamps):
        h = hour_vals[i]
        temp = 75 + 15 * math.sin(2 * math.pi * h / 24) + rng.normal(0, 2)
        demand = 5000 + 3000 * math.sin(2 * math.pi * h / 24) + rng.normal(0, 200)
        cost = 8 + 12 * max(0, math.sin(2 * math.pi * (h - 6) / 24)) + rng.normal(0, 1)
        rows.append({
            "timestamp": ts,
            "temperature_f": temp,
            "humidity": 60,
            "demand_mw": max(0, demand),
            "cost_cents_kwh": max(0, cost),
        })
    return pd.DataFrame(rows)


class TestSunShiftModel:
    @pytest.fixture(scope="class")
    def trained_model(self, tmp_path_factory):
        tmp_path = tmp_path_factory.mktemp("model")
        model = SunShiftModel()
        data = _synthetic_training_data(days=90)
        metrics = model.train(data)
        return model, metrics, tmp_path

    def test_train_returns_metrics(self, trained_model):
        _, metrics, _ = trained_model
        assert "mape" in metrics
        assert "mae" in metrics
        assert metrics["mape"] >= 0

    def test_train_metrics_have_sizes(self, trained_model):
        _, metrics, _ = trained_model
        assert "train_size" in metrics
        assert "test_size" in metrics
        assert metrics["train_size"] > 0
        assert metrics["test_size"] > 0

    def test_predict_returns_48_hours(self, trained_model):
        model, _, _ = trained_model
        data = _synthetic_training_data(days=10)
        predictions = model.predict(data.tail(48))
        assert len(predictions) == 48
        assert all(p >= 0 for p in predictions)

    def test_predict_returns_numpy_array(self, trained_model):
        model, _, _ = trained_model
        data = _synthetic_training_data(days=10)
        predictions = model.predict(data.tail(48))
        assert isinstance(predictions, np.ndarray)

    def test_save_and_load(self, trained_model):
        model, _, tmp_path = trained_model
        save_path = tmp_path / "model"
        model.save(save_path)

        # Verify expected files are written
        assert (save_path / "xgb_model.joblib").exists()
        assert (save_path / "prophet_model.json").exists()
        assert (save_path / "metrics.json").exists()

        loaded = SunShiftModel.load(save_path)
        data = _synthetic_training_data(days=10)
        original_preds = model.predict(data.tail(48))
        loaded_preds = loaded.predict(data.tail(48))
        np.testing.assert_array_almost_equal(original_preds, loaded_preds)

    def test_predict_raises_if_not_trained(self):
        model = SunShiftModel()
        data = _synthetic_training_data(days=10)
        with pytest.raises(RuntimeError, match="not trained"):
            model.predict(data.tail(48))

    def test_mape_reasonable(self, trained_model):
        """MAPE should be below 100% on simple sinusoidal synthetic data."""
        _, metrics, _ = trained_model
        assert metrics["mape"] < 1.0  # < 100%
