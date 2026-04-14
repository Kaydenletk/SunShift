"""Rich panels and boxes for demo UI."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_header() -> None:
    """Display the SunShift demo header."""
    from demo.ui.ascii_art import SUNSHIFT_LOGO
    console.print(SUNSHIFT_LOGO, style="bold cyan")


def show_scenario_title(number: int, title: str, story: str) -> None:
    """Display a scenario title with story context."""
    console.print()
    console.print(f"📊 Scenario {number}: {title}", style="bold white")
    console.print("─" * 50)
    console.print(f"[dim italic]{story}[/dim italic]")
    console.print()


def show_summary(title: str, items: dict[str, str]) -> None:
    """Display a summary panel with key-value pairs."""
    content = "\n".join(f"[bold]{k}:[/bold] {v}" for k, v in items.items())
    panel = Panel(content, title=title, border_style="green")
    console.print(panel)


def show_alert(message: str, severity: str = "warning") -> None:
    """Display an alert panel."""
    styles = {
        "warning": ("yellow", "⚠️"),
        "critical": ("red", "🚨"),
        "info": ("blue", "ℹ️"),
        "success": ("green", "✅"),
    }
    color, icon = styles.get(severity, ("white", "•"))
    panel = Panel(f"{icon} {message}", border_style=color)
    console.print(panel)


def show_savings(amount: float, period: str = "today") -> None:
    """Display savings highlight."""
    text = Text()
    text.append("💰 Savings ", style="bold")
    text.append(period.capitalize(), style="dim")
    text.append(": ", style="bold")
    text.append(f"${amount:.2f}", style="bold green")
    console.print(text)
