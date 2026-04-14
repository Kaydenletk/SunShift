"""Rich UI components for demo CLI."""

from demo.ui.panels import show_header, show_scenario_title, show_summary
from demo.ui.tables import workload_table, pricing_table, savings_table
from demo.ui.progress import migration_progress, loading_spinner
from demo.ui.ascii_art import SUNSHIFT_LOGO, HURRICANE_MAP

__all__ = [
    "show_header", "show_scenario_title", "show_summary",
    "workload_table", "pricing_table", "savings_table",
    "migration_progress", "loading_spinner",
    "SUNSHIFT_LOGO", "HURRICANE_MAP",
]
