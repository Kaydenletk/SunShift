"""Command dispatch route."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.core.deps import AgentStore
from backend.models.commands import AgentCommand, CommandResult

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/dispatch", response_model=CommandResult, status_code=status.HTTP_202_ACCEPTED)
def dispatch_command(command: AgentCommand, store: AgentStore) -> CommandResult:
    """Dispatch a command to a registered agent. Returns 404 for unknown agents."""
    if command.agent_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{command.agent_id}' not found.",
        )
    return CommandResult(
        command=command.command,
        agent_id=command.agent_id,
        status="queued",
        started_at=datetime.now(timezone.utc),
    )
