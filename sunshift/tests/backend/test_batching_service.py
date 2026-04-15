"""Tests for batching service.

This module tests the BatchingService which aggregates small workloads
into efficient batches for optimal scheduling.

Key behaviors tested:
- Small workloads (<50GB) are added to queue
- Queue flushes when: 2+ jobs OR 2h max wait time reached
- Large workloads (>=50GB) bypass queue and run solo
- Urgent workloads bypass queue regardless of size
- Batch job combines multiple workloads
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest

from backend.models.scheduler import (
    BatchQueue,
    CostWindow,
    Priority,
    RiskLevel,
    ScheduledJob,
    SchedulerSettings,
    TimeWindow,
    Workload,
    WorkloadType,
)
from backend.services.batching_service import (
    BYPASS_THRESHOLD_GB,
    MAX_BATCH_SIZE_GB,
    MIN_JOBS_TO_FLUSH,
    BatchingService,
)


def make_workload(
    workload_id: str = "wl-001",
    size_gb: int = 20,
    priority: Priority = Priority.NORMAL,
    workload_type: WorkloadType = WorkloadType.BACKUP,
    created_at: datetime | None = None,
) -> Workload:
    """Factory to create test workloads."""
    return Workload(
        id=workload_id,
        agent_id="agent-001",
        type=workload_type,
        size_gb=size_gb,
        priority=priority,
        deadline=None,
        created_at=created_at or datetime.now(timezone.utc),
    )


def make_cost_window(
    start_offset_hours: int = 0,
    duration_hours: int = 4,
    cost_cents: float = 8.0,
    confidence: float = 0.85,
) -> CostWindow:
    """Factory to create test cost windows."""
    now = datetime.now(timezone.utc)
    return CostWindow(
        start=now + timedelta(hours=start_offset_hours),
        end=now + timedelta(hours=start_offset_hours + duration_hours),
        avg_cost_cents_kwh=cost_cents,
        confidence=confidence,
        weather_risk=RiskLevel.LOW,
    )


class TestBatchingServiceConstants:
    """Tests to verify constants are defined correctly."""

    def test_bypass_threshold_is_50gb(self) -> None:
        """Large jobs threshold should be 50GB per spec."""
        assert BYPASS_THRESHOLD_GB == 50

    def test_max_batch_size_is_200gb(self) -> None:
        """Max batch size should be 200GB per spec."""
        assert MAX_BATCH_SIZE_GB == 200

    def test_min_jobs_to_flush_is_2(self) -> None:
        """Min jobs to trigger flush should be 2 per spec."""
        assert MIN_JOBS_TO_FLUSH == 2


class TestBatchingServiceAddToQueue:
    """Tests for adding workloads to the batch queue."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_adds_small_workload_to_queue(self, service: BatchingService) -> None:
        """Small workloads (<50GB) should be added to queue."""
        workload = make_workload(size_gb=20)
        result = service.add_to_queue(workload)

        assert result.queued is True
        assert result.bypass is False
        status = service.get_status()
        assert status.count == 1
        assert status.total_size_gb == 20

    def test_adds_multiple_small_workloads(self, service: BatchingService) -> None:
        """Multiple small workloads should accumulate in queue."""
        wl1 = make_workload(workload_id="wl-001", size_gb=15)
        wl2 = make_workload(workload_id="wl-002", size_gb=25)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        status = service.get_status()
        assert status.count == 2
        assert status.total_size_gb == 40

    def test_tracks_oldest_arrival_time(self, service: BatchingService) -> None:
        """Queue should track when the oldest workload arrived."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=1)
        new_time = datetime.now(timezone.utc)

        wl1 = make_workload(workload_id="wl-001", created_at=old_time)
        wl2 = make_workload(workload_id="wl-002", created_at=new_time)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        status = service.get_status()
        assert status.oldest_arrival == old_time


class TestBatchingServiceBypass:
    """Tests for workloads that bypass the queue."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_large_workload_bypasses_queue(self, service: BatchingService) -> None:
        """Large workloads (>=50GB) should bypass queue."""
        workload = make_workload(size_gb=50)  # Exactly at threshold
        result = service.add_to_queue(workload)

        assert result.bypass is True
        assert result.queued is False
        assert result.workload == workload
        status = service.get_status()
        assert status.count == 0

    def test_very_large_workload_bypasses_queue(self, service: BatchingService) -> None:
        """Very large workloads (>50GB) should bypass queue."""
        workload = make_workload(size_gb=100)
        result = service.add_to_queue(workload)

        assert result.bypass is True
        status = service.get_status()
        assert status.count == 0

    def test_urgent_workload_bypasses_queue(self, service: BatchingService) -> None:
        """Urgent workloads should bypass queue regardless of size."""
        workload = make_workload(size_gb=10, priority=Priority.URGENT)
        result = service.add_to_queue(workload)

        assert result.bypass is True
        assert result.queued is False
        status = service.get_status()
        assert status.count == 0

    def test_urgent_large_workload_bypasses_queue(
        self, service: BatchingService
    ) -> None:
        """Urgent large workloads should also bypass queue."""
        workload = make_workload(size_gb=100, priority=Priority.URGENT)
        result = service.add_to_queue(workload)

        assert result.bypass is True
        status = service.get_status()
        assert status.count == 0


class TestBatchingServiceFlushConditions:
    """Tests for queue flush conditions."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings (2h max wait)."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_should_not_flush_with_one_job(self, service: BatchingService) -> None:
        """Queue should not flush with only 1 job."""
        workload = make_workload(size_gb=20)
        service.add_to_queue(workload)

        assert service.should_flush() is False

    def test_flushes_when_min_jobs_reached(self, service: BatchingService) -> None:
        """Queue should flush when MIN_JOBS_TO_FLUSH (2) jobs are in queue."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        wl2 = make_workload(workload_id="wl-002", size_gb=25)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        assert service.should_flush() is True

    def test_flushes_after_max_wait_time(self, service: BatchingService) -> None:
        """Queue should flush after 2h max wait time, even with 1 job."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=2, minutes=1)
        workload = make_workload(created_at=old_time)
        service.add_to_queue(workload)

        assert service.should_flush() is True

    def test_does_not_flush_before_max_wait_time(
        self, service: BatchingService
    ) -> None:
        """Queue should not flush before 2h wait with only 1 job."""
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        workload = make_workload(created_at=recent_time)
        service.add_to_queue(workload)

        assert service.should_flush() is False

    def test_empty_queue_does_not_flush(self, service: BatchingService) -> None:
        """Empty queue should never flush."""
        assert service.should_flush() is False

    def test_flush_respects_aggressive_settings(self) -> None:
        """Aggressive settings should allow 4h max wait."""
        service = BatchingService(settings=SchedulerSettings.aggressive())

        # At 3h, should not flush (aggressive allows 4h)
        old_time = datetime.now(timezone.utc) - timedelta(hours=3)
        workload = make_workload(created_at=old_time)
        service.add_to_queue(workload)

        assert service.should_flush() is False

    def test_flush_respects_conservative_settings(self) -> None:
        """Conservative settings should allow only 1h max wait."""
        service = BatchingService(settings=SchedulerSettings.conservative())

        # At 1h+, should flush (conservative allows only 1h)
        old_time = datetime.now(timezone.utc) - timedelta(hours=1, minutes=1)
        workload = make_workload(created_at=old_time)
        service.add_to_queue(workload)

        assert service.should_flush() is True


class TestBatchingServiceCreateBatchJob:
    """Tests for creating batch jobs from queued workloads."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_create_batch_job_combines_workloads(
        self, service: BatchingService
    ) -> None:
        """Batch job should combine multiple workloads."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        wl2 = make_workload(workload_id="wl-002", size_gb=30)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        window = make_cost_window()
        batch_job = service.create_batch_job(window)

        assert batch_job is not None
        assert len(batch_job.workloads) == 2
        assert wl1 in batch_job.workloads
        assert wl2 in batch_job.workloads

    def test_create_batch_job_clears_queue(self, service: BatchingService) -> None:
        """Creating batch job should clear the queue."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        wl2 = make_workload(workload_id="wl-002", size_gb=30)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        window = make_cost_window()
        service.create_batch_job(window)

        status = service.get_status()
        assert status.count == 0
        assert status.total_size_gb == 0

    def test_create_batch_job_generates_unique_id(
        self, service: BatchingService
    ) -> None:
        """Batch job should have a unique ID."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        wl2 = make_workload(workload_id="wl-002", size_gb=30)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        window = make_cost_window()
        batch_job = service.create_batch_job(window)

        assert batch_job is not None
        assert batch_job.id.startswith("batch-")

    def test_create_batch_job_sets_time_window(self, service: BatchingService) -> None:
        """Batch job should have the correct time window from cost window."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        service.add_to_queue(wl1)
        service.add_to_queue(make_workload(workload_id="wl-002", size_gb=25))

        window = make_cost_window(start_offset_hours=2, duration_hours=3)
        batch_job = service.create_batch_job(window)

        assert batch_job is not None
        assert batch_job.window.start == window.start
        assert batch_job.window.end == window.end

    def test_create_batch_job_sets_confidence(self, service: BatchingService) -> None:
        """Batch job should inherit confidence from cost window."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        service.add_to_queue(wl1)
        service.add_to_queue(make_workload(workload_id="wl-002", size_gb=25))

        window = make_cost_window(confidence=0.92)
        batch_job = service.create_batch_job(window)

        assert batch_job is not None
        assert batch_job.confidence == 0.92

    def test_create_batch_job_returns_none_when_empty(
        self, service: BatchingService
    ) -> None:
        """Creating batch job from empty queue should return None."""
        window = make_cost_window()
        batch_job = service.create_batch_job(window)

        assert batch_job is None


class TestBatchingServiceCleanup:
    """Tests for cleanup functionality."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_cleanup_clears_queue(self, service: BatchingService) -> None:
        """Cleanup should clear all workloads from queue."""
        wl1 = make_workload(workload_id="wl-001", size_gb=20)
        wl2 = make_workload(workload_id="wl-002", size_gb=30)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        service.cleanup()

        status = service.get_status()
        assert status.count == 0
        assert status.total_size_gb == 0
        assert status.oldest_arrival is None

    def test_cleanup_on_empty_queue(self, service: BatchingService) -> None:
        """Cleanup on empty queue should not raise errors."""
        service.cleanup()  # Should not raise

        status = service.get_status()
        assert status.count == 0


class TestBatchingServiceGetStatus:
    """Tests for queue status retrieval."""

    @pytest.fixture
    def service(self) -> BatchingService:
        """Create a BatchingService with default settings."""
        return BatchingService(settings=SchedulerSettings.balanced())

    def test_get_status_empty_queue(self, service: BatchingService) -> None:
        """Empty queue should return zeroed status."""
        status = service.get_status()

        assert status.count == 0
        assert status.total_size_gb == 0
        assert status.oldest_arrival is None
        assert status.flush_at is None

    def test_get_status_with_workloads(self, service: BatchingService) -> None:
        """Queue with workloads should return accurate status."""
        created = datetime.now(timezone.utc)
        wl1 = make_workload(workload_id="wl-001", size_gb=20, created_at=created)
        wl2 = make_workload(workload_id="wl-002", size_gb=30)

        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        status = service.get_status()
        assert status.count == 2
        assert status.total_size_gb == 50
        assert status.oldest_arrival == created

    def test_get_status_includes_flush_at(self, service: BatchingService) -> None:
        """Status should include calculated flush_at time."""
        created = datetime.now(timezone.utc)
        workload = make_workload(created_at=created)
        service.add_to_queue(workload)

        status = service.get_status()
        # Balanced settings: 2h max wait
        expected_flush = created + timedelta(hours=2)
        assert status.flush_at is not None
        # Allow small time difference due to test execution
        assert abs((status.flush_at - expected_flush).total_seconds()) < 1
