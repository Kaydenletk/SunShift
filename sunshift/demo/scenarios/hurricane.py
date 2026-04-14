"""Scenario 2: Hurricane Shield Alert."""

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from demo.scenarios.base import BaseScenario, ScenarioResult
from demo.mock_data.weather import get_hurricane_data, get_hurricane_alert_message, get_recovery_plan
from demo.mock_data.workloads import get_workloads
from demo.ui.panels import show_alert
from demo.ui.ascii_art import HURRICANE_MAP
from demo.ui.progress import migration_progress, loading_spinner
from demo.utils.timing import sleep_with_option, set_quick_mode

console = Console()


class HurricaneScenario(BaseScenario):
    """Hurricane Shield Alert scenario."""

    name = "Hurricane Shield Alert"
    number = 2
    story = "Category 3 hurricane 'Elena' approaching Tampa Bay."

    def run(self) -> ScenarioResult:
        """Execute the hurricane scenario."""
        set_quick_mode(self.quick_mode)
        start_time = time.time()

        self.show_title()

        # Step 1: NOAA detection
        console.print("📡 [bold]NOAA NHC API[/bold] — Checking for active storms...")
        loading_spinner("Fetching storm data", duration=1.5 if not self.quick_mode else 0.3)

        hurricane = get_hurricane_data()
        console.print(f"[red bold]⚠️  STORM DETECTED: Hurricane {hurricane.name}[/red bold]")
        sleep_with_option(1.0)

        # Step 2: Show storm map
        console.print(HURRICANE_MAP)
        sleep_with_option(1.5)

        # Step 3: Threat evaluation
        console.print()
        console.print("🎯 [bold]Threat Evaluator[/bold] — Calculating risk score...")
        loading_spinner("Analyzing trajectory", duration=1.0 if not self.quick_mode else 0.2)

        threat_table = Table(title="Threat Assessment")
        threat_table.add_column("Metric", style="cyan")
        threat_table.add_column("Value", style="yellow")

        threat_table.add_row("Storm Category", f"[bold red]Category {hurricane.category}[/bold red]")
        threat_table.add_row("Wind Speed", f"{hurricane.wind_speed_mph} mph")
        threat_table.add_row("Distance", f"{hurricane.distance_miles:.0f} miles")
        threat_table.add_row("ETA", f"{hurricane.eta_hours:.1f} hours")
        threat_table.add_row("Risk Score", f"[bold red]{hurricane.risk_score * 100:.0f}%[/bold red]")

        console.print(threat_table)
        sleep_with_option(1.5)

        # Step 4: AI-generated alert
        console.print()
        console.print("🤖 [bold]Gemini API[/bold] — Generating executive alert...")
        loading_spinner("Composing alert", duration=1.0 if not self.quick_mode else 0.2)

        alert_message = get_hurricane_alert_message(hurricane)
        alert_panel = Panel(alert_message, title="🚨 HURRICANE ALERT", border_style="red")
        console.print(alert_panel)
        sleep_with_option(2.0)

        # Step 5: Trigger evacuation
        console.print()
        show_alert("Initiating preemptive workload evacuation", severity="critical")
        sleep_with_option(1.0)

        workloads = get_workloads()
        workload_names = [wl.name for wl in workloads]
        migration_progress(workload_names, delay=0.4 if self.quick_mode else 1.0)

        console.print()
        console.print("[bold green]✅ All workloads safely evacuated to AWS Ohio (us-east-2)[/bold green]")
        sleep_with_option(1.0)

        # Step 6: Show recovery plan
        console.print()
        console.print("📋 [bold]Recovery Plan[/bold]")

        recovery_table = Table()
        recovery_table.add_column("Step", style="cyan", width=6)
        recovery_table.add_column("Action", style="white")
        recovery_table.add_column("Status", style="green")

        for item in get_recovery_plan():
            status_style = "green" if item["status"] == "Complete" else "yellow"
            recovery_table.add_row(
                str(item["step"]),
                item["action"],
                f"[{status_style}]{item['status']}[/{status_style}]"
            )

        console.print(recovery_table)

        duration = time.time() - start_time

        self._result = ScenarioResult(
            name=self.name,
            success=True,
            savings=0,
            duration_seconds=duration,
            details={
                "hurricane_name": hurricane.name,
                "category": hurricane.category,
                "risk_score": hurricane.risk_score,
                "workloads_evacuated": len(workloads),
            }
        )

        return self._result
