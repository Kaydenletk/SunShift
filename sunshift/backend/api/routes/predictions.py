"""Prediction routes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from backend.core.deps import PredSvc, get_shield_orchestrator
from backend.models.prediction import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/energy", response_model=PredictionResponse)
async def get_energy_prediction(
    location: str = Query(default="tampa_fl", description="Location key for the prediction"),
    svc: PredSvc = None,
) -> PredictionResponse:
    """Return a 48-hour energy cost forecast with optimal scheduling windows."""
    response = svc.predict(location=location)
    # Merge live hurricane status
    try:
        shield_status = await get_shield_orchestrator().check()
        response.hurricane_status = {
            "active_threats": shield_status.active_threats,
            "shield_mode": shield_status.shield_mode,
        }
    except Exception:
        pass  # Keep default
    return response
