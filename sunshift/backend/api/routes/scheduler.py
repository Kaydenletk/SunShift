"""Scheduler API routes.

REST endpoints for the AI Scheduler:
- POST /scheduler/workloads - submit workload for scheduling
- GET /scheduler/schedule - get current schedule for agent
- PUT /scheduler/settings - update scheduler settings (mode presets)
- POST /scheduler/emergency - trigger emergency backup
- DELETE /scheduler/workloads/{id} - cancel workload
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from backend.models.scheduler import (
    WorkloadSubmitRequest,
    WorkloadSubmitResponse,
    ScheduleResponse,
    SettingsUpdateRequest,
    SettingsUpdateResponse,
    EmergencyRequest,
    EmergencyResponse,
    CancelResponse,
    SchedulerSettings,
    Workload,
    HourlyCost,
)
from backend.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# In-memory service instance (replace with DI in production)
_settings = SchedulerSettings.balanced()
_service = SchedulerService(_settings)
_workload_counter = 0


@router.post("/workloads", status_code=status.HTTP_201_CREATED, response_model=WorkloadSubmitResponse)
async def submit_workload(request: WorkloadSubmitRequest) -> WorkloadSubmitResponse:
    """Submit a new workload for scheduling.

    Args:
        request: Workload submission details.

    Returns:
        WorkloadSubmitResponse with workload_id and scheduling info.
    """
    global _workload_counter
    _workload_counter += 1

    workload = Workload(
        id=f"wl_{_workload_counter:06d}",
        agent_id=request.agent_id,
        type=request.type,
        size_gb=request.size_gb,
        priority=request.priority,
        deadline=request.deadline,
        created_at=datetime.now(timezone.utc),
    )

    job = await _service.schedule_workload(workload)

    if job:
        # Workload was scheduled immediately (large or urgent)
        return WorkloadSubmitResponse(
            workload_id=workload.id,
            scheduled_window=job.window,
            batch_queue_position=None,
            estimated_savings=Decimal("4.20"),  # TODO: Calculate from scorer
        )
    else:
        # Workload was added to batch queue
        status_info = _service.batching.get_status()
        return WorkloadSubmitResponse(
            workload_id=workload.id,
            scheduled_window=None,
            batch_queue_position=status_info.count,
            estimated_savings=Decimal("4.20"),  # TODO: Calculate from scorer
        )


@router.get("/schedule", response_model=ScheduleResponse)
async def get_schedule(agent_id: str) -> ScheduleResponse:
    """Get current schedule for an agent.

    Args:
        agent_id: ID of the agent to get schedule for.

    Returns:
        ScheduleResponse with jobs, batch queue, and cost forecast.
    """
    jobs = _service.get_scheduled_jobs(agent_id)
    batch_status = _service.batching.get_status()
    windows = _service.find_optimal_windows(48)

    # Generate cost forecast from windows
    cost_forecast = []
    for w in windows:
        cost_forecast.append(
            HourlyCost(
                hour=w.start,
                cost_cents_kwh=w.avg_cost_cents_kwh,
                confidence=w.confidence,
            )
        )

    return ScheduleResponse(
        jobs=jobs,
        next_window=windows[0] if windows else None,
        batch_queue_status=batch_status,
        cost_forecast=cost_forecast[:48],
    )


@router.put("/settings", response_model=SettingsUpdateResponse)
async def update_settings(request: SettingsUpdateRequest) -> SettingsUpdateResponse:
    """Update scheduler settings using preset mode.

    Args:
        request: Settings update with mode (conservative, balanced, aggressive).

    Returns:
        SettingsUpdateResponse with applied mode and effective settings.
    """
    global _settings, _service

    if request.mode == "conservative":
        _settings = SchedulerSettings.conservative()
    elif request.mode == "balanced":
        _settings = SchedulerSettings.balanced()
    elif request.mode == "aggressive":
        _settings = SchedulerSettings.aggressive()
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid mode. Must be one of: conservative, balanced, aggressive",
        )

    # Recreate service with new settings
    _service = SchedulerService(_settings)

    return SettingsUpdateResponse(
        mode=request.mode,
        effective_settings=_settings,
    )


@router.post("/emergency", response_model=EmergencyResponse)
async def trigger_emergency(request: EmergencyRequest) -> EmergencyResponse:
    """Trigger emergency backup for hurricane or manual override.

    Args:
        request: Emergency request with agent_id and reason.

    Returns:
        EmergencyResponse with job_id, status, and ETA.
    """
    job = await _service.trigger_emergency(request.agent_id, request.reason)

    return EmergencyResponse(
        job_id=job.id,
        status="executing",
        eta_minutes=15,  # Estimated based on typical workload size
    )


@router.delete("/workloads/{workload_id}", response_model=CancelResponse)
async def cancel_workload(workload_id: str) -> CancelResponse:
    """Cancel a workload by removing it from queue or scheduled jobs.

    Args:
        workload_id: ID of the workload to cancel.

    Returns:
        CancelResponse with cancellation status.

    Raises:
        HTTPException: 404 if workload not found, 400 if cannot cancel.
    """
    # Try to find and remove workload from batch queue
    # Access internal _workloads list directly
    workloads = _service.batching._workloads
    for i, wl in enumerate(workloads):
        if wl.id == workload_id:
            removed = workloads.pop(i)
            return CancelResponse(cancelled=True, refunded_to_queue=False)

    # Not found in queue, check scheduled jobs
    for job_id, job in _service._scheduled_jobs.items():
        for wl in job.workloads:
            if wl.id == workload_id:
                # Cannot cancel from scheduled job in MVP
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot cancel workload that is already scheduled. Job is in progress.",
                )

    # Workload not found anywhere
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Workload '{workload_id}' not found in queue or scheduled jobs.",
    )
