"""JSON export functionality."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def export_results(results: dict[str, Any], filepath: str | Path) -> Path:
    """Export demo results to JSON file."""
    filepath = Path(filepath)

    export_data = {
        "sunshift_demo": {
            "version": "0.1.0",
            "exported_at": datetime.now().isoformat(),
            "results": results,
        }
    }

    with open(filepath, "w") as f:
        json.dump(export_data, f, indent=2, default=str)

    return filepath


def format_results_summary(scenarios: list[dict]) -> dict:
    """Format scenario results for export."""
    total_savings = sum(s.get("savings", 0) for s in scenarios)

    return {
        "scenarios_run": len(scenarios),
        "total_savings": total_savings,
        "scenarios": scenarios,
        "summary": {
            "avg_savings_per_scenario": total_savings / len(scenarios) if scenarios else 0,
            "all_passed": all(s.get("success", False) for s in scenarios),
        }
    }
