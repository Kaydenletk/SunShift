"""Rich tables for demo data display."""

from rich.console import Console
from rich.table import Table

console = Console()


def workload_table(workloads: list[dict]) -> Table:
    """Create a workload status table."""
    table = Table(title="Current Workloads")
    table.add_column("Workload", style="cyan")
    table.add_column("Location", style="magenta")
    table.add_column("Status", style="green")

    for wl in workloads:
        status_style = "green" if wl["status"] == "Running" else "yellow"
        table.add_row(wl["name"], wl["location"], f"[{status_style}]{wl['status']}[/{status_style}]")

    return table


def pricing_table(current: float, off_peak: float, multiplier: float) -> Table:
    """Create an electricity pricing table."""
    table = Table(title="⚡ Electricity Pricing")
    table.add_column("Rate Type", style="cyan")
    table.add_column("Price", style="yellow")

    table.add_row("Current (PEAK)", f"[bold red]${current:.2f}/kWh[/bold red]")
    table.add_row("Off-Peak", f"[green]${off_peak:.2f}/kWh[/green]")
    table.add_row("Multiplier", f"[bold]{multiplier}x[/bold]")

    return table


def savings_table(local_cost: float, cloud_cost: float, savings: float) -> Table:
    """Create a cost comparison table."""
    table = Table(title="💰 Cost Comparison")
    table.add_column("Option", style="cyan")
    table.add_column("Cost", justify="right")

    table.add_row("Stay On-Prem", f"[red]${local_cost:.2f}[/red]")
    table.add_row("Migrate to AWS", f"[green]${cloud_cost:.2f}[/green]")
    table.add_row("Savings", f"[bold green]${savings:.2f}[/bold green]")

    return table


def weekly_cost_table(days: list[dict]) -> Table:
    """Create a weekly cost breakdown table."""
    table = Table(title="📅 Weekly Cost Breakdown")
    table.add_column("Day", style="cyan")
    table.add_column("Local Cost", justify="right")
    table.add_column("Cloud Cost", justify="right")
    table.add_column("Savings", justify="right", style="green")

    for day in days:
        savings = day["local"] - day["cloud"]
        table.add_row(
            day["name"],
            f"${day['local']:.2f}",
            f"${day['cloud']:.2f}",
            f"${savings:.2f}"
        )

    return table
