"""Base scenario class for demo CLI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console

console = Console()


@dataclass
class ScenarioResult:
    """Result of running a scenario."""
    name: str
    success: bool
    savings: float = 0.0
    duration_seconds: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class BaseScenario(ABC):
    """Abstract base class for demo scenarios."""

    name: str = "Base Scenario"
    number: int = 0
    story: str = ""

    def __init__(self, quick_mode: bool = False):
        """Initialize scenario."""
        self.quick_mode = quick_mode
        self._result: ScenarioResult | None = None

    @abstractmethod
    def run(self) -> ScenarioResult:
        """Execute the scenario and return results."""
        pass

    def show_title(self) -> None:
        """Display scenario title and story."""
        from demo.ui.panels import show_scenario_title
        show_scenario_title(self.number, self.name, self.story)

    def get_result(self) -> ScenarioResult | None:
        """Get the result of the last run."""
        return self._result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(quick_mode={self.quick_mode})"
