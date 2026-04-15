"""Pydantic models for the AI Scheduler system.

This module defines all data models for:
- Workloads: units of work to be scheduled
- ScheduledJobs: batched workloads with assigned time windows
- CostWindows: time periods with cost and risk information
- BatchQueues: holding area for workloads awaiting optimal windows
- API request/response schemas
"""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class WorkloadType(str, enum.Enum):
    """Type of workload to be scheduled."""

    BACKUP = "BACKUP"
    SYNC = "SYNC"
    AI_TRAIN = "AI_TRAIN"


class Priority(str, enum.Enum):
    """Priority level for workload scheduling."""

    NORMAL = "normal"
    URGENT = "urgent"


class JobStatus(str, enum.Enum):
    """Status of a scheduled job."""

    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """Weather/hurricane risk level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Workload(BaseModel):
    """A unit of work to be scheduled for cloud migration.

    Attributes:
        id: Unique identifier for this workload.
        agent_id: ID of the on-premise agent submitting this workload.
        type: Type of workload (BACKUP, SYNC, AI_TRAIN).
        size_gb: Size of data to transfer in gigabytes.
        priority: Scheduling priority (normal or urgent).
        deadline: Optional deadline by which workload must complete.
        created_at: Timestamp when workload was created.
    """

    id: str
    agent_id: str
    type: WorkloadType
    size_gb: int = Field(..., ge=0)
    priority: Priority = Priority.NORMAL
    deadline: datetime | None = None
    created_at: datetime


class TimeWindow(BaseModel):
    """A time window for scheduling.

    Attributes:
        start: Start time of the window.
        end: End time of the window.
    """

    start: datetime
    end: datetime


class CostWindow(BaseModel):
    """A time window with associated cost and risk information.

    Attributes:
        start: Start time of the window.
        end: End time of the window.
        avg_cost_cents_kwh: Average electricity cost in cents per kWh.
        confidence: Confidence level of cost prediction (0-1).
        score: Computed score for this window (higher is better).
        weather_risk: Hurricane/weather risk level.
    """

    start: datetime
    end: datetime
    avg_cost_cents_kwh: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    score: float = Field(default=0)
    weather_risk: RiskLevel = RiskLevel.LOW


class ScheduledJob(BaseModel):
    """A job that has been scheduled for execution.

    Attributes:
        id: Unique identifier for this job.
        workloads: List of workloads batched in this job.
        window: Time window when job will execute.
        estimated_cost: Estimated cost in dollars.
        confidence: Confidence level in the schedule (0-1).
        status: Current status of the job.
    """

    id: str
    workloads: list[Workload]
    window: TimeWindow
    estimated_cost: Decimal = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    status: JobStatus = JobStatus.SCHEDULED


class BatchQueue(BaseModel):
    """Queue of workloads waiting to be batched and scheduled.

    Attributes:
        workloads: List of workloads in the queue.
        total_size_gb: Total size of all queued workloads.
        oldest_arrival: Timestamp of oldest workload in queue.
        target_window: Target cost window for batch execution.
        flush_at: Deadline to flush queue regardless of cost.
    """

    workloads: list[Workload] = Field(default_factory=list)
    total_size_gb: int = Field(default=0, ge=0)
    oldest_arrival: datetime | None = None
    target_window: CostWindow | None = None
    flush_at: datetime | None = None


class BatchQueueStatus(BaseModel):
    """Summary status of the batch queue for API responses.

    Attributes:
        count: Number of workloads in queue.
        total_size_gb: Total size of queued workloads.
        oldest_arrival: Timestamp of oldest workload.
        flush_at: Scheduled flush time.
        target_window_start: Start of target execution window.
    """

    count: int = 0
    total_size_gb: int = 0
    oldest_arrival: datetime | None = None
    flush_at: datetime | None = None
    target_window_start: datetime | None = None


# =============================================================================
# API Request/Response Models
# =============================================================================


class WorkloadSubmitRequest(BaseModel):
    """Request to submit a new workload for scheduling.

    Attributes:
        agent_id: ID of the submitting agent.
        type: Type of workload.
        size_gb: Size of data in gigabytes (must be >= 1).
        priority: Scheduling priority.
        deadline: Optional deadline for completion.
    """

    agent_id: str
    type: WorkloadType
    size_gb: int = Field(..., ge=1)
    priority: Priority = Priority.NORMAL
    deadline: datetime | None = None


class WorkloadSubmitResponse(BaseModel):
    """Response after submitting a workload.

    Attributes:
        workload_id: Assigned workload ID.
        scheduled_window: Assigned execution window (if immediately scheduled).
        batch_queue_position: Position in batch queue (if queued).
        estimated_savings: Estimated cost savings in dollars.
    """

    workload_id: str
    scheduled_window: TimeWindow | None = None
    batch_queue_position: int | None = None
    estimated_savings: Decimal


class HourlyCost(BaseModel):
    """Hourly cost forecast entry.

    Attributes:
        hour: Hour timestamp.
        cost_cents_kwh: Forecasted cost in cents per kWh.
        confidence: Confidence in this forecast (0-1).
    """

    hour: datetime
    cost_cents_kwh: float
    confidence: float


class ScheduleResponse(BaseModel):
    """Response containing current schedule state.

    Attributes:
        jobs: List of scheduled jobs.
        next_window: Next optimal execution window.
        batch_queue_status: Current batch queue status.
        cost_forecast: Hourly cost forecast.
    """

    jobs: list[ScheduledJob]
    next_window: CostWindow | None = None
    batch_queue_status: BatchQueueStatus
    cost_forecast: list[HourlyCost]


class SchedulerSettings(BaseModel):
    """Configuration settings for the scheduler.

    Attributes:
        min_confidence: Minimum confidence threshold for scheduling.
        lookahead_hours: Hours to look ahead for cost windows.
        batch_wait_max_hours: Maximum hours to wait for batching.
        replan_frequency_hours: How often to recalculate schedule.
        hurricane_trigger_level: Alert level that triggers emergency mode.
    """

    min_confidence: float = Field(default=0.75, ge=0, le=1)
    lookahead_hours: int = Field(default=48, ge=1, le=168)
    batch_wait_max_hours: int = Field(default=2, ge=1, le=12)
    replan_frequency_hours: int = Field(default=6, ge=1, le=24)
    hurricane_trigger_level: str = Field(default="warning")

    @classmethod
    def conservative(cls) -> SchedulerSettings:
        """Create conservative settings: high confidence, short lookahead.

        Best for risk-averse users who prioritize reliability over savings.
        """
        return cls(
            min_confidence=0.90,
            lookahead_hours=24,
            batch_wait_max_hours=1,
            replan_frequency_hours=2,
            hurricane_trigger_level="watch",
        )

    @classmethod
    def balanced(cls) -> SchedulerSettings:
        """Create balanced settings: moderate confidence and lookahead.

        Good default for most users balancing savings and reliability.
        """
        return cls(
            min_confidence=0.75,
            lookahead_hours=48,
            batch_wait_max_hours=2,
            replan_frequency_hours=6,
            hurricane_trigger_level="warning",
        )

    @classmethod
    def aggressive(cls) -> SchedulerSettings:
        """Create aggressive settings: lower confidence, longer batching.

        Best for users prioritizing maximum cost savings over timing.
        """
        return cls(
            min_confidence=0.60,
            lookahead_hours=48,
            batch_wait_max_hours=4,
            replan_frequency_hours=12,
            hurricane_trigger_level="warning",
        )


class SettingsUpdateRequest(BaseModel):
    """Request to update scheduler settings.

    Attributes:
        mode: Preset mode to apply (conservative, balanced, aggressive).
    """

    mode: str = Field(..., pattern=r"^(conservative|balanced|aggressive)$")


class SettingsUpdateResponse(BaseModel):
    """Response after updating settings.

    Attributes:
        mode: Applied mode name.
        effective_settings: The actual settings now in effect.
    """

    mode: str
    effective_settings: SchedulerSettings


class EmergencyRequest(BaseModel):
    """Request to trigger emergency sync.

    Attributes:
        agent_id: ID of the agent requesting emergency sync.
        reason: Reason for emergency (hurricane or manual).
    """

    agent_id: str
    reason: str = Field(..., pattern=r"^(hurricane|manual)$")


class EmergencyResponse(BaseModel):
    """Response after triggering emergency sync.

    Attributes:
        job_id: ID of the emergency job created.
        status: Current status of the emergency job.
        eta_minutes: Estimated time to completion in minutes.
    """

    job_id: str
    status: str = "executing"
    eta_minutes: int


class CancelResponse(BaseModel):
    """Response after cancelling a job.

    Attributes:
        cancelled: Whether cancellation was successful.
        refunded_to_queue: Whether workloads were returned to queue.
    """

    cancelled: bool
    refunded_to_queue: bool = False
