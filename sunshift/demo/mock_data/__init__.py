"""Mock data generators for demo scenarios."""

from demo.mock_data.pricing import get_pricing_data, PricingData
from demo.mock_data.workloads import get_workloads, Workload
from demo.mock_data.weather import get_hurricane_data, HurricaneData
from demo.mock_data.predictions import get_predictions, PredictionData

__all__ = [
    "get_pricing_data", "PricingData",
    "get_workloads", "Workload",
    "get_hurricane_data", "HurricaneData",
    "get_predictions", "PredictionData",
]
