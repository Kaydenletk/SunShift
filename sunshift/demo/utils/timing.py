"""Animation timing helpers."""

import time

NORMAL_DELAY = 1.0
QUICK_DELAY = 0.2

_quick_mode = False


def set_quick_mode(enabled: bool) -> None:
    """Enable or disable quick mode globally."""
    global _quick_mode
    _quick_mode = enabled


def get_delay(base: float = NORMAL_DELAY) -> float:
    """Get delay based on current mode."""
    if _quick_mode:
        return min(base * 0.2, QUICK_DELAY)
    return base


def sleep_with_option(seconds: float) -> None:
    """Sleep with quick mode support."""
    time.sleep(get_delay(seconds))


def countdown(seconds: int, message: str = "Starting in") -> None:
    """Display countdown timer."""
    from rich.console import Console
    console = Console()

    for i in range(seconds, 0, -1):
        console.print(f"\r{message} {i}...", end="")
        time.sleep(get_delay(1.0))
    console.print(f"\r{message} Go!    ")
