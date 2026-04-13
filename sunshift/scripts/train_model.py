#!/usr/bin/env python3
"""Train SunShift ML model on historical data.

Usage:
    uv run scripts/train_model.py
    uv run scripts/train_model.py --data data/historical_training_data.parquet --output models/latest

The script expects a Parquet file with columns:
    timestamp, temperature_f, humidity, demand_mw, cost_cents_kwh
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow running as a script from the sunshift/ root
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from backend.ml.model import SunShiftModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("train_model")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train SunShift Prophet + XGBoost ensemble")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/historical_training_data.parquet"),
        help="Path to historical training data (Parquet format)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/latest"),
        help="Directory to save trained model artifacts",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.2,
        help="Fraction of data to use as hold-out test set (default: 0.2)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.data.exists():
        logger.error("Training data not found at %s", args.data)
        logger.error("Run scripts/collect_historical_data.py first.")
        sys.exit(1)

    logger.info("Loading training data from %s", args.data)
    data = pd.read_parquet(args.data)
    logger.info("Loaded %d rows of training data", len(data))

    required_cols = {"timestamp", "temperature_f", "humidity", "demand_mw", "cost_cents_kwh"}
    missing = required_cols - set(data.columns)
    if missing:
        logger.error("Missing required columns: %s", missing)
        sys.exit(1)

    model = SunShiftModel()
    logger.info("Training ensemble (Prophet + XGBoost) with test_ratio=%.2f …", args.test_ratio)
    metrics = model.train(data, test_ratio=args.test_ratio)

    logger.info("Training complete.")
    logger.info("  MAPE : %.4f (%.2f%%)", metrics["mape"], metrics["mape"] * 100)
    logger.info("  MAE  : %.4f cents/kWh", metrics["mae"])
    logger.info("  Train: %d rows | Test: %d rows", metrics["train_size"], metrics["test_size"])

    model.save(args.output)
    logger.info("Model artifacts saved to %s", args.output)


if __name__ == "__main__":
    main()
