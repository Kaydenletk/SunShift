"""Hurricane Shield routes."""
from __future__ import annotations

from fastapi import APIRouter

from backend.core.deps import get_shield_orchestrator

router = APIRouter(prefix="/hurricane", tags=["hurricane"])


@router.get("/status")
async def get_hurricane_status() -> dict:
    """Return current Hurricane Shield status with threat assessment."""
    orchestrator = get_shield_orchestrator()
    status = await orchestrator.check()
    return {
        "shield_mode": status.shield_mode,
        "active_threats": status.active_threats,
        "max_threat_level": status.max_threat_level.value,
        "storms": [
            {"name": s.name, "category": s.category, "wind_mph": s.wind_mph}
            for s in status.storms
        ],
        "last_check": status.last_check,
        "alert_message": status.alert_message,
    }


@router.post("/demo/activate")
async def activate_demo() -> dict:
    """Activate demo mode with a simulated storm."""
    orchestrator = get_shield_orchestrator()
    orchestrator.activate_demo()
    status = await orchestrator.check()
    return {"status": "demo_activated", "shield_mode": status.shield_mode}


@router.post("/demo/deactivate")
async def deactivate_demo() -> dict:
    """Deactivate demo mode and return to standby."""
    orchestrator = get_shield_orchestrator()
    orchestrator.deactivate_demo()
    return {"status": "demo_deactivated", "shield_mode": "standby"}
