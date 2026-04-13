"""Dependency injection — in-memory stores for MVP."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends

from backend.models.agent import AgentStatus
from backend.models.metrics import MetricsPayload
from backend.ml.predict import PredictionService


# ---------------------------------------------------------------------------
# In-memory stores (module-level singletons)
# ---------------------------------------------------------------------------

_agent_store: dict[str, AgentStatus] = {}
_metrics_store: list[MetricsPayload] = []
_prediction_service: PredictionService | None = None


# ---------------------------------------------------------------------------
# Store accessors (injected via FastAPI Depends)
# ---------------------------------------------------------------------------


def get_agent_store() -> dict[str, AgentStatus]:
    return _agent_store


def get_metrics_store() -> list[MetricsPayload]:
    return _metrics_store


def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service


# ---------------------------------------------------------------------------
# Type aliases for clean injection signatures
# ---------------------------------------------------------------------------

AgentStore = Annotated[dict[str, AgentStatus], Depends(get_agent_store)]
MetricsStore = Annotated[list[MetricsPayload], Depends(get_metrics_store)]
PredSvc = Annotated[PredictionService, Depends(get_prediction_service)]
