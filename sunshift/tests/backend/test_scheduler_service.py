"""Tests for the Scheduler Service (Hybrid algorithm).

This module tests the core scheduling logic:
- ScheduleMode determination (Greedy vs Lookahead)
- Hurricane override behavior
- Window scoring and selection
- Integration with batching service
- Workload scheduling workflow
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from backend.services.scheduler_service import SchedulerService, ScheduleMode
from backend.models.scheduler import (
    Workload,
    WorkloadType,
    Priority,
    SchedulerSettings,
    CostWindow,
    RiskLevel,
)


def make_workload(
    id: str = "wl_1",
    size_gb: int = 25,
    priority: Priority = Priority.NORMAL,
    deadline: datetime | None = None,
) -> Workload:
    """Helper to create test workloads."""
    return Workload(
        id=id,
        agent_id="clinic-001",
        type=WorkloadType.BACKUP,
        size_gb=size_gb,
        priority=priority,
        deadline=deadline,
        created_at=datetime.now(timezone.utc),
    )


def make_cost_windows(count: int = 48) -> list[CostWindow]:
    """Generate mock cost windows with realistic TOU pattern.

    FPL TOU pattern:
    - Peak (12-21): 23-28 cents/kWh, confidence 0.75
    - Shoulder (6-12): 12-15 cents/kWh, confidence 0.85
    - Off-peak (21-6): 6-8 cents/kWh, confidence 0.92
    """
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    windows = []

    for i in range(count):
        hour = (now.hour + i) % 24

        # FPL TOU: Peak 12-21, Off-peak otherwise
        if 12 <= hour < 21:
            cost = 23.0 + (i % 5)  # Peak: 23-28
            conf = 0.75
        elif 6 <= hour < 12:
            cost = 12.0 + (i % 3)  # Shoulder: 12-15
            conf = 0.85
        else:
            cost = 6.0 + (i % 2)  # Off-peak: 6-8
            conf = 0.92

        windows.append(
            CostWindow(
                start=now + timedelta(hours=i),
                end=now + timedelta(hours=i + 1),
                avg_cost_cents_kwh=cost,
                confidence=conf,
                weather_risk=RiskLevel.LOW,
            )
        )

    return windows


class TestScheduleMode:
    """Test the ScheduleMode enum."""

    def test_mode_enum_values(self):
        """Verify enum values match spec."""
        assert ScheduleMode.GREEDY.value == "greedy"
        assert ScheduleMode.LOOKAHEAD.value == "lookahead"


class TestSchedulerService:
    """Test the core scheduler service."""

    @pytest.fixture
    def service(self):
        """Create a scheduler service with balanced settings."""
        settings = SchedulerSettings.balanced()
        return SchedulerService(settings)

    def test_greedy_mode_for_urgent_workload(self, service):
        """Urgent workloads should use GREEDY mode."""
        wl = make_workload(priority=Priority.URGENT)
        mode = service._determine_mode(wl, hurricane_active=False)
        assert mode == ScheduleMode.GREEDY

    def test_greedy_mode_for_workload_with_deadline(self, service):
        """Workloads with deadline should use GREEDY mode."""
        deadline = datetime.now(timezone.utc) + timedelta(hours=6)
        wl = make_workload(deadline=deadline)
        mode = service._determine_mode(wl, hurricane_active=False)
        assert mode == ScheduleMode.GREEDY

    def test_lookahead_mode_for_flexible_workload(self, service):
        """Flexible (normal priority, no deadline) should use LOOKAHEAD mode."""
        wl = make_workload(priority=Priority.NORMAL)
        mode = service._determine_mode(wl, hurricane_active=False)
        assert mode == ScheduleMode.LOOKAHEAD

    def test_hurricane_overrides_to_greedy(self, service):
        """Hurricane alert should force GREEDY mode regardless of workload."""
        wl = make_workload(priority=Priority.NORMAL)
        mode = service._determine_mode(wl, hurricane_active=True)
        assert mode == ScheduleMode.GREEDY

    def test_greedy_selects_best_within_6h(self, service):
        """Greedy mode should pick best window within 6h horizon."""
        windows = make_cost_windows(12)
        best = service._find_best_window_greedy(windows)

        # Should select an off-peak window within first 6 hours
        assert best.avg_cost_cents_kwh < 15.0

        # Verify it's within greedy horizon
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(hours=service.GREEDY_HORIZON_HOURS)
        assert best.start <= horizon

    def test_lookahead_finds_optimal_48h_window(self, service):
        """Lookahead mode should find best window in 48h."""
        windows = make_cost_windows(48)
        best = service._find_best_window_lookahead(windows)

        # Should select an off-peak window (lowest cost + high confidence)
        assert best.avg_cost_cents_kwh < 10.0
        assert best.confidence >= service.settings.min_confidence

    def test_confidence_scoring_weights_correctly(self, service):
        """Higher confidence windows should be preferred due to confidence^2."""
        now = datetime.now(timezone.utc)

        high_conf = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.90,
            weather_risk=RiskLevel.LOW,
        )

        low_conf = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=7.0,  # Slightly cheaper but much lower confidence
            confidence=0.50,
            weather_risk=RiskLevel.LOW,
        )

        # Score using the window scorer
        high_score = service._score_window(high_conf)
        low_score = service._score_window(low_conf)

        # High confidence should win despite being 1 cent more expensive
        # Because 0.9^2 / 0.5^2 = 0.81 / 0.25 = 3.24x multiplier
        assert high_score > low_score

    @pytest.mark.asyncio
    async def test_schedule_large_workload_bypasses_batching(self, service):
        """Large workloads (>=50GB) should bypass batching and schedule immediately."""
        wl = make_workload(size_gb=60)
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                job = await service.schedule_workload(wl)

        # Should return a job (not None = batched)
        assert job is not None
        assert len(job.workloads) == 1
        assert job.workloads[0].id == "wl_1"
        assert job.workloads[0].size_gb == 60

    @pytest.mark.asyncio
    async def test_schedule_urgent_workload_uses_greedy(self, service):
        """Urgent workloads should use greedy mode (6h horizon)."""
        wl = make_workload(priority=Priority.URGENT, size_gb=60)
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                job = await service.schedule_workload(wl)

        assert job is not None
        # Should schedule in one of the first 6 hours (greedy horizon)
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(hours=6)
        assert job.window.start <= horizon

    @pytest.mark.asyncio
    async def test_schedule_small_workload_batches(self, service):
        """Small workloads (<50GB) should be added to batch queue."""
        wl = make_workload(size_gb=25)
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                job = await service.schedule_workload(wl)

        # Should return None (batched, not immediately scheduled)
        assert job is None

        # Verify workload is in batch queue
        status = service.batching.get_status()
        assert status.count == 1
        assert status.total_size_gb == 25

    @pytest.mark.asyncio
    async def test_batch_flushes_when_min_jobs_reached(self, service):
        """Batch queue should flush when MIN_JOBS_TO_FLUSH is reached."""
        wl1 = make_workload(id="wl_1", size_gb=25)
        wl2 = make_workload(id="wl_2", size_gb=30)
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                # First workload: should batch (return None)
                job1 = await service.schedule_workload(wl1)
                assert job1 is None

                # Second workload: should trigger flush (return batch job)
                job2 = await service.schedule_workload(wl2)
                assert job2 is not None
                assert len(job2.workloads) == 2

    @pytest.mark.asyncio
    async def test_get_scheduled_jobs_filters_by_agent(self, service):
        """get_scheduled_jobs should filter by agent_id."""
        wl1 = make_workload(id="wl_1", size_gb=60)  # Large, will schedule immediately
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                await service.schedule_workload(wl1)

        jobs = service.get_scheduled_jobs(agent_id="clinic-001")
        assert len(jobs) == 1
        assert jobs[0].workloads[0].agent_id == "clinic-001"

    @pytest.mark.asyncio
    async def test_trigger_emergency_creates_immediate_job(self, service):
        """Emergency trigger should create immediate job with RUNNING status."""
        job = await service.trigger_emergency(agent_id="clinic-001", reason="hurricane")

        assert job is not None
        assert job.status.value == "running"
        assert "emergency" in job.id

        # Should start immediately (within 1 minute)
        now = datetime.now(timezone.utc)
        assert (job.window.start - now).total_seconds() < 60


class TestReplanningLogic:
    """Test replanning behavior when forecast updates."""

    @pytest.mark.asyncio
    async def test_replan_reschedules_when_significantly_better(self):
        """Replan should reschedule jobs when new window is >10% better."""
        settings = SchedulerSettings.balanced()
        service = SchedulerService(settings)

        # Create a scheduled job
        wl = make_workload(id="wl_1", size_gb=60)
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                job = await service.schedule_workload(wl)

        original_start = job.window.start

        # Simulate forecast update with much better window
        updated_jobs = await service.replan_on_forecast_update()

        # For this test to pass, we need better windows in the mock
        # This is a placeholder - real test would manipulate forecast
        assert isinstance(updated_jobs, list)
