"""CLI entry point for SunShift demo."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from demo.ui.panels import show_header
from demo.utils.timing import set_quick_mode
from demo.utils.export import export_results, format_results_summary

app = typer.Typer(
    name="sunshift-demo",
    help="SunShift Demo CLI — Interactive showcase of AI-powered compute optimization",
    add_completion=False,
)

console = Console()


def get_scenario_class(name: str):
    """Get scenario class by name."""
    from demo.scenarios import SCENARIOS
    return SCENARIOS.get(name)


@app.command()
def main(
    scenario: Optional[str] = typer.Option(
        None,
        "--scenario", "-s",
        help="Run specific scenario: peak, hurricane, analytics",
    ),
    quick: bool = typer.Option(
        False,
        "--quick", "-q",
        help="Run with faster animations",
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export", "-e",
        help="Export results to JSON file",
    ),
    all_scenarios: bool = typer.Option(
        False,
        "--all", "-a",
        help="Run all scenarios",
    ),
) -> None:
    """Run the SunShift demo."""
    set_quick_mode(quick)

    show_header()

    results = []

    if scenario:
        # Run specific scenario
        scenario_class = get_scenario_class(scenario)
        if not scenario_class:
            console.print(f"[red]Unknown scenario: {scenario}[/red]")
            console.print("Available: peak, hurricane, analytics")
            raise typer.Exit(1)

        instance = scenario_class(quick_mode=quick)
        result = instance.run()
        results.append(result.__dict__)

    elif all_scenarios:
        # Run all scenarios
        from demo.scenarios import SCENARIOS

        for name, scenario_class in SCENARIOS.items():
            instance = scenario_class(quick_mode=quick)
            result = instance.run()
            results.append(result.__dict__)
            console.print()
            console.print("─" * 60)
            console.print()

    else:
        # Interactive menu
        console.print("Select scenario:")
        console.print("  [bold][1][/bold] Peak Hour Cost Optimization")
        console.print("  [bold][2][/bold] Hurricane Shield Alert")
        console.print("  [bold][3][/bold] Weekly Analytics Report")
        console.print("  [bold][A][/bold] Run All Scenarios")
        console.print()

        choice = typer.prompt("Enter choice", default="1")

        scenario_map = {"1": "peak", "2": "hurricane", "3": "analytics"}

        if choice.upper() == "A":
            from demo.scenarios import SCENARIOS
            for name, scenario_class in SCENARIOS.items():
                instance = scenario_class(quick_mode=quick)
                result = instance.run()
                results.append(result.__dict__)
                console.print()
                console.print("─" * 60)
                console.print()
        elif choice in scenario_map:
            scenario_name = scenario_map[choice]
            scenario_class = get_scenario_class(scenario_name)
            instance = scenario_class(quick_mode=quick)
            result = instance.run()
            results.append(result.__dict__)
        else:
            console.print(f"[red]Invalid choice: {choice}[/red]")
            raise typer.Exit(1)

    # Export if requested
    if export and results:
        summary = format_results_summary(results)
        output_path = export_results(summary, export)
        console.print()
        console.print(f"[green]Results exported to: {output_path}[/green]")

    # Final summary
    if results:
        console.print()
        console.print("━" * 60)
        total_savings = sum(r.get("savings", 0) for r in results)
        console.print(f"[bold]Demo Complete![/bold] Total savings demonstrated: [green]${total_savings:.2f}[/green]")


if __name__ == "__main__":
    app()
