"""Agent registration and status routes."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.core.deps import AgentStore
from backend.models.agent import AgentRegistration, AgentStatus

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/register", response_model=AgentStatus, status_code=status.HTTP_201_CREATED)
def register_agent(payload: AgentRegistration, store: AgentStore) -> AgentStatus:
    """Register a new agent. Returns 409 if agent_id already exists."""
    if payload.agent_id in store:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent '{payload.agent_id}' is already registered.",
        )
    agent_status = AgentStatus(
        agent_id=payload.agent_id,
        status="online",
        last_seen=datetime.now(timezone.utc),
    )
    store[payload.agent_id] = agent_status
    return agent_status


@router.get("/status/{agent_id}", response_model=AgentStatus)
def get_agent_status(agent_id: str, store: AgentStore) -> AgentStatus:
    """Return status for a known agent. Returns 404 for unknown agents."""
    if agent_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found.",
        )
    return store[agent_id]
