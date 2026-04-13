"""SunShift FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

from backend.core.config import settings
from backend.api.routes.agents import router as agents_router
from backend.api.routes.metrics import router as metrics_router
from backend.api.routes.predictions import router as predictions_router
from backend.api.routes.commands import router as commands_router
from backend.api.websocket import router as ws_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-Powered Compute Cost Optimizer — SP1 API",
    debug=settings.debug,
)

# ---------------------------------------------------------------------------
# Mount REST routers under /api/v1
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(agents_router, prefix=API_PREFIX)
app.include_router(metrics_router, prefix=API_PREFIX)
app.include_router(predictions_router, prefix=API_PREFIX)
app.include_router(commands_router, prefix=API_PREFIX)

# ---------------------------------------------------------------------------
# Mount WebSocket router (no prefix — path defined in router itself)
# ---------------------------------------------------------------------------
app.include_router(ws_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
