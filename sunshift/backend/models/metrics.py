from datetime import datetime
from pydantic import BaseModel, Field


class MetricsPayload(BaseModel):
    agent_id: str
    timestamp: datetime
    cpu_percent: float = Field(..., ge=0, le=100)
    memory_percent: float = Field(..., ge=0, le=100)
    disk_percent: float = Field(..., ge=0, le=100)
    network_bytes_sent: int = Field(..., ge=0)
    network_bytes_recv: int = Field(..., ge=0)
    estimated_power_watts: float = Field(default=0, ge=0)
