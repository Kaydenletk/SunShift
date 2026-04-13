from datetime import datetime
from pydantic import BaseModel, Field


class HourlyForecast(BaseModel):
    hour: datetime
    cost_cents_kwh: float = Field(..., ge=0)
    demand_mw: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)


class OptimalWindow(BaseModel):
    rank: int
    start: datetime
    end: datetime
    avg_cost_cents_kwh: float
    estimated_savings_dollars: float
    workload_recommendation: str = Field(..., pattern=r"^(FULL_SYNC|INCREMENTAL_SYNC|AI_TRAINING)$")


class PredictionResponse(BaseModel):
    prediction_id: str
    location: str
    generated_at: datetime
    model_version: str
    hourly_forecast: list[HourlyForecast]
    optimal_windows: list[OptimalWindow]
    explanation: str
    hurricane_status: dict = Field(default_factory=lambda: {"active_threats": 0, "shield_mode": "standby"})
