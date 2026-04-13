from datetime import datetime
from pydantic import BaseModel, Field


class AgentCommand(BaseModel):
    command: str = Field(..., pattern=r"^(START_SYNC|FULL_BACKUP|STOP|INCREMENTAL_SYNC)$")
    agent_id: str
    issued_at: datetime
    paths: list[str] = Field(default_factory=list)
    priority: str = Field(default="normal", pattern=r"^(low|normal|high|critical)$")


class CommandResult(BaseModel):
    command: str
    agent_id: str
    status: str = Field(..., pattern=r"^(success|failed|in_progress|queued)$")
    started_at: datetime
    completed_at: datetime | None = None
    bytes_transferred: int = 0
    error_message: str | None = None
