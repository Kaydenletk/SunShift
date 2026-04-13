from datetime import datetime
from pydantic import BaseModel, Field


class AgentRegistration(BaseModel):
    agent_id: str = Field(..., pattern=r"^[a-z0-9\-]+$", max_length=64)
    name: str = Field(..., max_length=128)
    location: str = Field(default="tampa_fl")
    watch_paths: list[str] = Field(default_factory=list)


class AgentStatus(BaseModel):
    agent_id: str
    status: str = Field(..., pattern=r"^(online|offline|syncing|error)$")
    last_seen: datetime
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_percent: float | None = None
    last_sync: datetime | None = None
    bytes_synced: int = 0
