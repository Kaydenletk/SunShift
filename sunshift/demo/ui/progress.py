"""Progress bars and spinners for demo animations."""

import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def migration_progress(workloads: list[str], delay: float = 0.5) -> None:
    """Animate workload migration with progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating workloads to AWS Ohio...", total=len(workloads))

        for workload in workloads:
            time.sleep(delay)
            progress.update(task, advance=1, description=f"Migrating {workload}...")

        progress.update(task, description="Migration complete!")


def loading_spinner(message: str, duration: float = 2.0) -> None:
    """Show a loading spinner for the given duration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description=message, total=None)
        time.sleep(duration)


def savings_counter(target: float, duration: float = 2.0, prefix: str = "Savings") -> None:
    """Animate a savings counter from 0 to target."""
    steps = 20
    step_value = target / steps
    step_delay = duration / steps

    current = 0.0
    for _ in range(steps):
        current += step_value
        console.print(f"\r💰 {prefix}: ${current:.2f}", end="")
        time.sleep(step_delay)

    console.print(f"\r💰 {prefix}: ${target:.2f} ", style="bold green")
