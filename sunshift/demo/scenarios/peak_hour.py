"""Scenario 1: Peak Hour Cost Optimization."""

import time

from rich.console import Console

from demo.scenarios.base import BaseScenario, ScenarioResult
from demo.mock_data.pricing import get_pricing_data
from demo.mock_data.workloads import get_workloads, get_workloads_as_dicts, calculate_hourly_savings
from demo.ui.panels import show_alert
from demo.ui.tables import workload_table, pricing_table, savings_table
from demo.ui.progress import migration_progress, savings_counter
from demo.utils.timing import sleep_with_option, set_quick_mode

console = Console()


class PeakHourScenario(BaseScenario):
    """Peak Hour Cost Optimization scenario."""

    name = "Peak Hour Cost Optimization"
    number = 1
    story = "It's 2 PM on a Tuesday. FPL TOU peak pricing kicks in."

    def run(self) -> ScenarioResult:
        """Execute the peak hour scenario."""
        set_quick_mode(self.quick_mode)
        start_time = time.time()

        self.show_title()

        # Step 1: Show current time and workloads
        console.print(f"Current Time: [bold]2:00 PM EDT[/bold] (Peak Hours: 12 PM - 9 PM)")
        console.print()
        sleep_with_option(1.0)

        workloads = get_workloads()
        console.print(workload_table(get_workloads_as_dicts()))
        sleep_with_option(1.5)

        # Step 2: Display electricity pricing
        pricing = get_pricing_data(current_hour=14)
        console.print()
        console.print(pricing_table(pricing.current_rate, pricing.off_peak_rate, pricing.multiplier))
        sleep_with_option(1.5)

        # Step 3: Show Prophet prediction
        console.print()
        console.print("🔮 [bold]Prophet Prediction:[/bold] Peak pricing continues until 9 PM")
        sleep_with_option(1.0)

        # Step 4: Recommend migration
        console.print()
        show_alert("Recommending workload migration to AWS Ohio", severity="info")
        sleep_with_option(1.0)

        # Step 5: Animate migration
        console.print()
        workload_names = [wl.name for wl in workloads]
        migration_progress(workload_names, delay=0.3 if self.quick_mode else 0.8)
        sleep_with_option(0.5)

        # Step 6: Calculate and show savings
        hourly_savings = calculate_hourly_savings(workloads)
        peak_hours_remaining = 7  # 2 PM to 9 PM
        total_savings = hourly_savings * peak_hours_remaining

        console.print()
        local_cost = sum(wl.hourly_cost_local for wl in workloads) * peak_hours_remaining
        cloud_cost = sum(wl.hourly_cost_cloud for wl in workloads) * peak_hours_remaining
        console.print(savings_table(local_cost, cloud_cost, total_savings))

        console.print()
        savings_counter(total_savings, duration=1.5 if not self.quick_mode else 0.3, prefix="Savings Today")

        duration = time.time() - start_time

        self._result = ScenarioResult(
            name=self.name,
            success=True,
            savings=total_savings,
            duration_seconds=duration,
            details={
                "workloads_migrated": len(workloads),
                "peak_hours_avoided": peak_hours_remaining,
                "hourly_savings": hourly_savings,
            }
        )

        return self._result
