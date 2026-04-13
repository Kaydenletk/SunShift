"""Metrics ingestion route."""
from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from backend.core.deps import MetricsStore
from backend.models.metrics import MetricsPayload

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_metrics(payload: MetricsPayload, store: MetricsStore) -> JSONResponse:
    """Accept validated metrics payload and store it."""
    store.append(payload)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"accepted": True, "agent_id": payload.agent_id},
    )
