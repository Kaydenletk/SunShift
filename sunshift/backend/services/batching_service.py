"""Batching service for aggregating small workloads.

This service implements the batching logic for the AI Scheduler:
- Small workloads (<50GB) are queued for batching
- Large workloads (>=50GB) or urgent workloads bypass the queue
- Queue flushes when: MIN_JOBS_TO_FLUSH reached OR max wait time exceeded
- Batch jobs combine multiple workloads for efficient scheduling
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.models.scheduler import (
    BatchQueueStatus,
    CostWindow,
    JobStatus,
    Priority,
    ScheduledJob,
    SchedulerSettings,
    TimeWindow,
    Workload,
)

# Constants per specification
BYPASS_THRESHOLD_GB: int = 50
MAX_BATCH_SIZE_GB: int = 200
MIN_JOBS_TO_FLUSH: int = 2


@dataclass
class AddToQueueResult:
    """Result of adding a workload to the queue.

    Attributes:
        queued: True if workload was added to queue.
        bypass: True if workload bypassed queue (large or urgent).
        workload: The workload that was processed.
    """

    queued: bool
    bypass: bool
    workload: Workload


class BatchingService:
    """Service for batching small workloads into efficient batches.

    Aggregates small workloads (<50GB) and flushes when either:
    - MIN_JOBS_TO_FLUSH (2) workloads are queued, OR
    - Max wait time (from settings) is exceeded

    Large workloads (>=50GB) and urgent workloads bypass the queue.
    """

    def __init__(self, settings: SchedulerSettings) -> None:
        """Initialize the batching service.

        Args:
            settings: Scheduler settings controlling batch behavior.
        """
        self._settings = settings
        self._workloads: list[Workload] = []
        self._oldest_arrival: datetime | None = None

    def add_to_queue(self, workload: Workload) -> AddToQueueResult:
        """Add a workload to the batch queue or bypass if applicable.

        Args:
            workload: The workload to process.

        Returns:
            Result indicating whether workload was queued or bypassed.
        """
        # Urgent workloads bypass regardless of size
        if workload.priority == Priority.URGENT:
            return AddToQueueResult(queued=False, bypass=True, workload=workload)

        # Large workloads bypass the queue
        if workload.size_gb >= BYPASS_THRESHOLD_GB:
            return AddToQueueResult(queued=False, bypass=True, workload=workload)

        # Add to queue
        self._workloads.append(workload)

        # Track oldest arrival time
        if self._oldest_arrival is None or workload.created_at < self._oldest_arrival:
            self._oldest_arrival = workload.created_at

        return AddToQueueResult(queued=True, bypass=False, workload=workload)

    def get_status(self) -> BatchQueueStatus:
        """Get current status of the batch queue.

        Returns:
            Status including count, total size, oldest arrival, and flush time.
        """
        if not self._workloads:
            return BatchQueueStatus(
                count=0,
                total_size_gb=0,
                oldest_arrival=None,
                flush_at=None,
            )

        total_size = sum(w.size_gb for w in self._workloads)

        # Calculate flush_at based on oldest arrival + max wait time
        flush_at = None
        if self._oldest_arrival is not None:
            flush_at = self._oldest_arrival + timedelta(
                hours=self._settings.batch_wait_max_hours
            )

        return BatchQueueStatus(
            count=len(self._workloads),
            total_size_gb=total_size,
            oldest_arrival=self._oldest_arrival,
            flush_at=flush_at,
        )

    def should_flush(self) -> bool:
        """Check if the queue should be flushed.

        Returns True when either:
        - MIN_JOBS_TO_FLUSH (2) or more workloads are queued
        - Max wait time has been exceeded (even with 1 job)

        Returns:
            True if queue should be flushed, False otherwise.
        """
        if not self._workloads:
            return False

        # Condition 1: Minimum jobs reached
        if len(self._workloads) >= MIN_JOBS_TO_FLUSH:
            return True

        # Condition 2: Max wait time exceeded
        if self._oldest_arrival is not None:
            max_wait = timedelta(hours=self._settings.batch_wait_max_hours)
            if datetime.now(timezone.utc) - self._oldest_arrival >= max_wait:
                return True

        return False

    def create_batch_job(self, window: CostWindow) -> ScheduledJob | None:
        """Create a batch job from queued workloads.

        Args:
            window: The cost window to schedule the batch in.

        Returns:
            ScheduledJob containing all queued workloads, or None if queue is empty.
        """
        if not self._workloads:
            return None

        # Create the batch job
        job_id = f"batch-{uuid.uuid4().hex[:8]}"
        workloads = list(self._workloads)

        # Estimate cost (placeholder - real calculation would involve data transfer costs)
        estimated_cost = Decimal("0.00")

        job = ScheduledJob(
            id=job_id,
            workloads=workloads,
            window=TimeWindow(start=window.start, end=window.end),
            estimated_cost=estimated_cost,
            confidence=window.confidence,
            status=JobStatus.SCHEDULED,
        )

        # Clear the queue
        self._workloads = []
        self._oldest_arrival = None

        return job

    def cleanup(self) -> None:
        """Clear all workloads from the queue."""
        self._workloads = []
        self._oldest_arrival = None
