"""Prediction routes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from backend.core.deps import PredSvc
from backend.models.prediction import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/energy", response_model=PredictionResponse)
def get_energy_prediction(
    location: str = Query(default="tampa_fl", description="Location key for the prediction"),
    svc: PredSvc = None,
) -> PredictionResponse:
    """Return a 48-hour energy cost forecast with optimal scheduling windows."""
    return svc.predict(location=location)
