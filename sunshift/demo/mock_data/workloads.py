"""VM/container workload mock data."""

from dataclasses import dataclass


@dataclass
class Workload:
    """Workload representation."""
    name: str
    location: str
    status: str
    cpu_usage: float
    memory_gb: float
    hourly_cost_local: float
    hourly_cost_cloud: float


def get_workloads() -> list[Workload]:
    """Get mock workload data for demo."""
    return [
        Workload(
            name="web-server-01",
            location="On-Prem",
            status="Running",
            cpu_usage=45.2,
            memory_gb=4.0,
            hourly_cost_local=2.50,
            hourly_cost_cloud=0.85,
        ),
        Workload(
            name="api-server-01",
            location="On-Prem",
            status="Running",
            cpu_usage=62.8,
            memory_gb=8.0,
            hourly_cost_local=3.20,
            hourly_cost_cloud=1.10,
        ),
        Workload(
            name="db-replica-01",
            location="On-Prem",
            status="Running",
            cpu_usage=28.5,
            memory_gb=16.0,
            hourly_cost_local=4.80,
            hourly_cost_cloud=1.60,
        ),
    ]


def get_workloads_as_dicts() -> list[dict]:
    """Get workloads as dictionaries for table display."""
    return [
        {"name": wl.name, "location": wl.location, "status": wl.status}
        for wl in get_workloads()
    ]


def calculate_hourly_savings(workloads: list[Workload]) -> float:
    """Calculate hourly savings from migration."""
    local_total = sum(wl.hourly_cost_local for wl in workloads)
    cloud_total = sum(wl.hourly_cost_cloud for wl in workloads)
    return local_total - cloud_total
