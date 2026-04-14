"""Hurricane/storm mock data."""

from dataclasses import dataclass


@dataclass
class HurricaneData:
    """Hurricane tracking data."""
    name: str
    category: int
    wind_speed_mph: int
    distance_miles: float
    direction: str
    eta_hours: float
    risk_score: float
    recommended_action: str


def get_hurricane_data() -> HurricaneData:
    """Get mock hurricane data for demo."""
    return HurricaneData(
        name="Elena",
        category=3,
        wind_speed_mph=125,
        distance_miles=200,
        direction="NNE",
        eta_hours=18.5,
        risk_score=0.78,
        recommended_action="EVACUATE_WORKLOADS",
    )


def get_hurricane_alert_message(data: HurricaneData) -> str:
    """Generate executive alert message for hurricane."""
    return f"""
🚨 HURRICANE ALERT — CATEGORY {data.category}

Hurricane {data.name} is currently {data.distance_miles:.0f} miles from Tampa Bay,
moving {data.direction} at approximately 12 mph.

CURRENT CONDITIONS:
• Maximum sustained winds: {data.wind_speed_mph} mph
• Estimated arrival: {data.eta_hours:.1f} hours
• Threat assessment: {data.risk_score * 100:.0f}% risk score

RECOMMENDED ACTION: {data.recommended_action.replace('_', ' ')}

SunShift is initiating preemptive workload migration to AWS Ohio (us-east-2)
to ensure business continuity during the storm.
"""


def get_recovery_plan() -> list[dict]:
    """Get post-storm recovery plan."""
    return [
        {"step": 1, "action": "Monitor storm progress", "status": "Complete"},
        {"step": 2, "action": "Verify AWS workload health", "status": "Complete"},
        {"step": 3, "action": "Assess on-prem infrastructure", "status": "Pending"},
        {"step": 4, "action": "Restore local operations", "status": "Pending"},
        {"step": 5, "action": "Migrate workloads back", "status": "Pending"},
    ]
