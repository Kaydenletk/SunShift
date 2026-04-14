"""Scenario 3: Weekly Analytics Report."""

import time

from rich.console import Console
from rich.panel import Panel

from demo.scenarios.base import BaseScenario, ScenarioResult
from demo.mock_data.predictions import get_prediction_accuracy, get_weekly_summary
from demo.ui.panels import show_summary
from demo.ui.tables import weekly_cost_table
from demo.utils.timing import sleep_with_option, set_quick_mode

console = Console()


class AnalyticsScenario(BaseScenario):
    """Weekly Analytics Report scenario."""

    name = "Weekly Analytics Report"
    number = 3
    story = "End of week summary for business owner."

    def run(self) -> ScenarioResult:
        """Execute the analytics scenario."""
        set_quick_mode(self.quick_mode)
        start_time = time.time()

        self.show_title()

        # Step 1: Display 7-day cost history
        console.print("📊 [bold]7-Day Cost History[/bold]")
        console.print()
        sleep_with_option(0.5)

        weekly_data = get_weekly_summary()
        console.print(weekly_cost_table(weekly_data))
        sleep_with_option(1.5)

        # Calculate totals
        total_local = sum(d["local"] for d in weekly_data)
        total_cloud = sum(d["cloud"] for d in weekly_data)
        total_savings = total_local - total_cloud

        console.print()
        console.print(f"[bold]Weekly Totals:[/bold]")
        console.print(f"  Local costs avoided: [red]${total_local:.2f}[/red]")
        console.print(f"  Cloud costs incurred: [yellow]${total_cloud:.2f}[/yellow]")
        console.print(f"  [bold green]Net savings: ${total_savings:.2f}[/bold green]")
        sleep_with_option(1.0)

        # Step 2: Show prediction accuracy
        console.print()
        console.print("🎯 [bold]Prediction Accuracy[/bold]")
        console.print()

        accuracy = get_prediction_accuracy()

        accuracy_panel = Panel(
            f"""
[bold]Prophet + XGBoost Ensemble Performance[/bold]

Overall Accuracy: [bold green]{accuracy['accuracy_percent']:.1f}%[/bold green]

Detailed Metrics:
• Mean Absolute Error (MAE): ${accuracy['mae']:.3f}/kWh
• Root Mean Square Error (RMSE): ${accuracy['rmse']:.3f}/kWh
• Mean Absolute Percentage Error (MAPE): {accuracy['mape']:.1f}%
            """,
            title="📈 ML Model Performance",
            border_style="blue"
        )
        console.print(accuracy_panel)
        sleep_with_option(1.5)

        # Step 3: Savings vs always-on-cloud
        console.print()
        console.print("💡 [bold]Savings Analysis[/bold]")
        console.print()

        always_cloud_cost = total_cloud * 1.4
        hybrid_savings = always_cloud_cost - total_cloud

        comparison = {
            "Always On-Prem": f"${total_local:.2f}",
            "Always On-Cloud": f"${always_cloud_cost:.2f}",
            "SunShift Hybrid": f"${total_cloud:.2f}",
            "Savings vs On-Prem": f"${total_savings:.2f} ({(total_savings/total_local)*100:.0f}%)",
            "Savings vs Always-Cloud": f"${hybrid_savings:.2f} ({(hybrid_savings/always_cloud_cost)*100:.0f}%)",
        }
        show_summary("Cost Comparison", comparison)
        sleep_with_option(1.0)

        # Step 4: Recommendations
        console.print()
        console.print("🔮 [bold]Next Week Forecast[/bold]")
        console.print()

        recommendations = Panel(
            """
Based on historical patterns and weather forecast:

• [bold]Expected peak hours:[/bold] 63 hours (Mon-Sun, 12PM-9PM)
• [bold]Predicted savings:[/bold] $180-220
• [bold]Hurricane risk:[/bold] Low (no active systems)

[bold green]Recommendation:[/bold green] Continue automated optimization.
No manual intervention required.
            """,
            title="📋 Recommendations",
            border_style="green"
        )
        console.print(recommendations)

        duration = time.time() - start_time

        self._result = ScenarioResult(
            name=self.name,
            success=True,
            savings=total_savings,
            duration_seconds=duration,
            details={
                "total_local_cost": total_local,
                "total_cloud_cost": total_cloud,
                "prediction_accuracy": accuracy["accuracy_percent"],
                "days_analyzed": len(weekly_data),
            }
        )

        return self._result
