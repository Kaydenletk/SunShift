"""Scenario registry for demo CLI."""

from demo.scenarios.base import BaseScenario
from demo.scenarios.peak_hour import PeakHourScenario
from demo.scenarios.hurricane import HurricaneScenario
from demo.scenarios.analytics import AnalyticsScenario

SCENARIOS = {
    "peak": PeakHourScenario,
    "hurricane": HurricaneScenario,
    "analytics": AnalyticsScenario,
}

__all__ = ["BaseScenario", "SCENARIOS", "PeakHourScenario", "HurricaneScenario", "AnalyticsScenario"]
