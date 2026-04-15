"""Tests for scheduler Pydantic models.

TDD: Write tests first, then implement models.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pydantic import ValidationError

from backend.models.scheduler import (
    WorkloadType,
    Priority,
    JobStatus,
    RiskLevel,
    Workload,
    TimeWindow,
    CostWindow,
    ScheduledJob,
    BatchQueue,
    BatchQueueStatus,
    WorkloadSubmitRequest,
    WorkloadSubmitResponse,
    ScheduleResponse,
    SettingsUpdateRequest,
    SettingsUpdateResponse,
    SchedulerSettings,
    EmergencyRequest,
    EmergencyResponse,
    CancelResponse,
    HourlyCost,
)


class TestEnums:
    """Test enum definitions."""

    def test_workload_type_values(self):
        assert WorkloadType.BACKUP == "BACKUP"
        assert WorkloadType.SYNC == "SYNC"
        assert WorkloadType.AI_TRAIN == "AI_TRAIN"

    def test_priority_values(self):
        assert Priority.NORMAL == "normal"
        assert Priority.URGENT == "urgent"

    def test_job_status_values(self):
        assert JobStatus.SCHEDULED == "scheduled"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"

    def test_risk_level_values(self):
        assert RiskLevel.LOW == "low"
        assert RiskLevel.MEDIUM == "medium"
        assert RiskLevel.HIGH == "high"


class TestWorkload:
    """Test Workload model."""

    def test_valid_workload(self):
        wl = Workload(
            id="wl_abc123",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
            priority=Priority.NORMAL,
            created_at=datetime.now(timezone.utc),
        )
        assert wl.id == "wl_abc123"
        assert wl.agent_id == "clinic-001"
        assert wl.type == WorkloadType.BACKUP
        assert wl.size_gb == 50
        assert wl.priority == Priority.NORMAL
        assert wl.deadline is None

    def test_workload_with_deadline(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=6)
        wl = Workload(
            id="wl_urgent",
            agent_id="clinic-001",
            type=WorkloadType.SYNC,
            size_gb=10,
            priority=Priority.URGENT,
            deadline=deadline,
            created_at=datetime.now(timezone.utc),
        )
        assert wl.deadline == deadline
        assert wl.priority == Priority.URGENT

    def test_rejects_negative_size(self):
        with pytest.raises(ValidationError):
            Workload(
                id="wl_bad",
                agent_id="clinic-001",
                type=WorkloadType.BACKUP,
                size_gb=-10,
                priority=Priority.NORMAL,
                created_at=datetime.now(timezone.utc),
            )

    def test_allows_zero_size(self):
        wl = Workload(
            id="wl_zero",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=0,
            priority=Priority.NORMAL,
            created_at=datetime.now(timezone.utc),
        )
        assert wl.size_gb == 0

    def test_rejects_invalid_workload_type(self):
        with pytest.raises(ValidationError):
            Workload(
                id="wl_bad",
                agent_id="clinic-001",
                type="INVALID_TYPE",
                size_gb=50,
                priority=Priority.NORMAL,
                created_at=datetime.now(timezone.utc),
            )


class TestTimeWindow:
    """Test TimeWindow model."""

    def test_valid_time_window(self):
        now = datetime.now(timezone.utc)
        tw = TimeWindow(
            start=now,
            end=now + timedelta(hours=2),
        )
        assert tw.start == now
        assert tw.end == now + timedelta(hours=2)


class TestCostWindow:
    """Test CostWindow model."""

    def test_valid_cost_window(self):
        now = datetime.now(timezone.utc)
        cw = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.5,
            confidence=0.92,
            score=7.19,
            weather_risk=RiskLevel.LOW,
        )
        assert cw.confidence == 0.92
        assert cw.avg_cost_cents_kwh == 8.5
        assert cw.score == 7.19
        assert cw.weather_risk == RiskLevel.LOW

    def test_rejects_confidence_over_1(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            CostWindow(
                start=now,
                end=now + timedelta(hours=4),
                avg_cost_cents_kwh=8.5,
                confidence=1.5,
                score=7.19,
                weather_risk=RiskLevel.LOW,
            )

    def test_rejects_negative_confidence(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            CostWindow(
                start=now,
                end=now + timedelta(hours=4),
                avg_cost_cents_kwh=8.5,
                confidence=-0.1,
                score=7.19,
                weather_risk=RiskLevel.LOW,
            )

    def test_rejects_negative_cost(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            CostWindow(
                start=now,
                end=now + timedelta(hours=4),
                avg_cost_cents_kwh=-1.0,
                confidence=0.92,
                score=7.19,
                weather_risk=RiskLevel.LOW,
            )

    def test_default_score_and_risk(self):
        now = datetime.now(timezone.utc)
        cw = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.5,
            confidence=0.92,
        )
        assert cw.score == 0
        assert cw.weather_risk == RiskLevel.LOW


class TestScheduledJob:
    """Test ScheduledJob model."""

    def test_valid_scheduled_job(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_1",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
            priority=Priority.NORMAL,
            created_at=now,
        )
        job = ScheduledJob(
            id="job_xyz789",
            workloads=[wl],
            window=TimeWindow(start=now, end=now + timedelta(hours=2)),
            estimated_cost=Decimal("12.50"),
            confidence=0.85,
            status=JobStatus.SCHEDULED,
        )
        assert len(job.workloads) == 1
        assert job.status == JobStatus.SCHEDULED
        assert job.estimated_cost == Decimal("12.50")
        assert job.confidence == 0.85

    def test_job_with_multiple_workloads(self):
        now = datetime.now(timezone.utc)
        workloads = [
            Workload(
                id=f"wl_{i}",
                agent_id="clinic-001",
                type=WorkloadType.BACKUP,
                size_gb=25,
                priority=Priority.NORMAL,
                created_at=now,
            )
            for i in range(3)
        ]
        job = ScheduledJob(
            id="job_multi",
            workloads=workloads,
            window=TimeWindow(start=now, end=now + timedelta(hours=4)),
            estimated_cost=Decimal("35.00"),
            confidence=0.80,
            status=JobStatus.RUNNING,
        )
        assert len(job.workloads) == 3
        assert job.status == JobStatus.RUNNING

    def test_rejects_negative_estimated_cost(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_1",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
            priority=Priority.NORMAL,
            created_at=now,
        )
        with pytest.raises(ValidationError):
            ScheduledJob(
                id="job_bad",
                workloads=[wl],
                window=TimeWindow(start=now, end=now + timedelta(hours=2)),
                estimated_cost=Decimal("-5.00"),
                confidence=0.85,
                status=JobStatus.SCHEDULED,
            )


class TestBatchQueue:
    """Test BatchQueue model."""

    def test_valid_batch_queue(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_1",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=25,
            priority=Priority.NORMAL,
            created_at=now,
        )
        bq = BatchQueue(
            workloads=[wl],
            total_size_gb=25,
            oldest_arrival=now,
            flush_at=now + timedelta(hours=2),
        )
        assert bq.total_size_gb == 25
        assert len(bq.workloads) == 1
        assert bq.flush_at is not None

    def test_empty_batch_queue(self):
        bq = BatchQueue()
        assert bq.workloads == []
        assert bq.total_size_gb == 0
        assert bq.oldest_arrival is None
        assert bq.target_window is None
        assert bq.flush_at is None

    def test_batch_queue_with_target_window(self):
        now = datetime.now(timezone.utc)
        target = CostWindow(
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3),
            avg_cost_cents_kwh=6.0,
            confidence=0.88,
        )
        bq = BatchQueue(
            workloads=[],
            total_size_gb=0,
            target_window=target,
        )
        assert bq.target_window is not None
        assert bq.target_window.avg_cost_cents_kwh == 6.0


class TestBatchQueueStatus:
    """Test BatchQueueStatus model."""

    def test_default_status(self):
        status = BatchQueueStatus()
        assert status.count == 0
        assert status.total_size_gb == 0
        assert status.oldest_arrival is None
        assert status.flush_at is None
        assert status.target_window_start is None

    def test_status_with_values(self):
        now = datetime.now(timezone.utc)
        status = BatchQueueStatus(
            count=5,
            total_size_gb=150,
            oldest_arrival=now - timedelta(hours=1),
            flush_at=now + timedelta(hours=1),
            target_window_start=now + timedelta(hours=2),
        )
        assert status.count == 5
        assert status.total_size_gb == 150


class TestWorkloadSubmitRequest:
    """Test WorkloadSubmitRequest model."""

    def test_valid_request(self):
        req = WorkloadSubmitRequest(
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
        )
        assert req.agent_id == "clinic-001"
        assert req.type == WorkloadType.BACKUP
        assert req.size_gb == 50
        assert req.priority == Priority.NORMAL
        assert req.deadline is None

    def test_request_with_priority_and_deadline(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=4)
        req = WorkloadSubmitRequest(
            agent_id="clinic-001",
            type=WorkloadType.SYNC,
            size_gb=20,
            priority=Priority.URGENT,
            deadline=deadline,
        )
        assert req.priority == Priority.URGENT
        assert req.deadline == deadline

    def test_rejects_invalid_type(self):
        with pytest.raises(ValidationError):
            WorkloadSubmitRequest(
                agent_id="clinic-001",
                type="INVALID",
                size_gb=50,
            )

    def test_rejects_zero_size(self):
        with pytest.raises(ValidationError):
            WorkloadSubmitRequest(
                agent_id="clinic-001",
                type=WorkloadType.BACKUP,
                size_gb=0,
            )

    def test_rejects_negative_size(self):
        with pytest.raises(ValidationError):
            WorkloadSubmitRequest(
                agent_id="clinic-001",
                type=WorkloadType.BACKUP,
                size_gb=-10,
            )


class TestWorkloadSubmitResponse:
    """Test WorkloadSubmitResponse model."""

    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = WorkloadSubmitResponse(
            workload_id="wl_abc123",
            scheduled_window=TimeWindow(start=now, end=now + timedelta(hours=2)),
            estimated_savings=Decimal("5.50"),
        )
        assert resp.workload_id == "wl_abc123"
        assert resp.scheduled_window is not None
        assert resp.batch_queue_position is None

    def test_response_with_batch_queue_position(self):
        resp = WorkloadSubmitResponse(
            workload_id="wl_xyz789",
            batch_queue_position=3,
            estimated_savings=Decimal("3.25"),
        )
        assert resp.batch_queue_position == 3
        assert resp.scheduled_window is None


class TestHourlyCost:
    """Test HourlyCost model."""

    def test_valid_hourly_cost(self):
        now = datetime.now(timezone.utc)
        hc = HourlyCost(
            hour=now,
            cost_cents_kwh=8.5,
            confidence=0.92,
        )
        assert hc.hour == now
        assert hc.cost_cents_kwh == 8.5
        assert hc.confidence == 0.92


class TestScheduleResponse:
    """Test ScheduleResponse model."""

    def test_valid_schedule_response(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_1",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
            priority=Priority.NORMAL,
            created_at=now,
        )
        job = ScheduledJob(
            id="job_1",
            workloads=[wl],
            window=TimeWindow(start=now, end=now + timedelta(hours=2)),
            estimated_cost=Decimal("12.50"),
            confidence=0.85,
            status=JobStatus.SCHEDULED,
        )
        resp = ScheduleResponse(
            jobs=[job],
            batch_queue_status=BatchQueueStatus(count=2, total_size_gb=75),
            cost_forecast=[
                HourlyCost(hour=now, cost_cents_kwh=8.5, confidence=0.9),
                HourlyCost(hour=now + timedelta(hours=1), cost_cents_kwh=7.2, confidence=0.88),
            ],
        )
        assert len(resp.jobs) == 1
        assert resp.next_window is None
        assert resp.batch_queue_status.count == 2
        assert len(resp.cost_forecast) == 2


class TestSchedulerSettings:
    """Test SchedulerSettings model and presets."""

    def test_default_settings(self):
        settings = SchedulerSettings()
        assert settings.min_confidence == 0.75
        assert settings.lookahead_hours == 48
        assert settings.batch_wait_max_hours == 2
        assert settings.replan_frequency_hours == 6
        assert settings.hurricane_trigger_level == "warning"

    def test_balanced_preset(self):
        settings = SchedulerSettings.balanced()
        assert settings.min_confidence == 0.75
        assert settings.lookahead_hours == 48
        assert settings.batch_wait_max_hours == 2

    def test_conservative_preset(self):
        settings = SchedulerSettings.conservative()
        assert settings.min_confidence == 0.90
        assert settings.lookahead_hours == 24
        assert settings.batch_wait_max_hours == 1
        assert settings.replan_frequency_hours == 2
        assert settings.hurricane_trigger_level == "watch"

    def test_aggressive_preset(self):
        settings = SchedulerSettings.aggressive()
        assert settings.min_confidence == 0.60
        assert settings.lookahead_hours == 48
        assert settings.batch_wait_max_hours == 4
        assert settings.replan_frequency_hours == 12

    def test_rejects_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            SchedulerSettings(min_confidence=1.5)
        with pytest.raises(ValidationError):
            SchedulerSettings(min_confidence=-0.1)

    def test_rejects_lookahead_out_of_range(self):
        with pytest.raises(ValidationError):
            SchedulerSettings(lookahead_hours=0)
        with pytest.raises(ValidationError):
            SchedulerSettings(lookahead_hours=200)


class TestSettingsUpdateRequest:
    """Test SettingsUpdateRequest model."""

    def test_valid_conservative_mode(self):
        req = SettingsUpdateRequest(mode="conservative")
        assert req.mode == "conservative"

    def test_valid_balanced_mode(self):
        req = SettingsUpdateRequest(mode="balanced")
        assert req.mode == "balanced"

    def test_valid_aggressive_mode(self):
        req = SettingsUpdateRequest(mode="aggressive")
        assert req.mode == "aggressive"

    def test_rejects_invalid_mode(self):
        with pytest.raises(ValidationError):
            SettingsUpdateRequest(mode="invalid_mode")


class TestSettingsUpdateResponse:
    """Test SettingsUpdateResponse model."""

    def test_valid_response(self):
        settings = SchedulerSettings.balanced()
        resp = SettingsUpdateResponse(
            mode="balanced",
            effective_settings=settings,
        )
        assert resp.mode == "balanced"
        assert resp.effective_settings.min_confidence == 0.75


class TestEmergencyRequest:
    """Test EmergencyRequest model."""

    def test_hurricane_emergency(self):
        req = EmergencyRequest(
            agent_id="clinic-001",
            reason="hurricane",
        )
        assert req.agent_id == "clinic-001"
        assert req.reason == "hurricane"

    def test_manual_emergency(self):
        req = EmergencyRequest(
            agent_id="clinic-001",
            reason="manual",
        )
        assert req.reason == "manual"

    def test_rejects_invalid_reason(self):
        with pytest.raises(ValidationError):
            EmergencyRequest(
                agent_id="clinic-001",
                reason="invalid_reason",
            )


class TestEmergencyResponse:
    """Test EmergencyResponse model."""

    def test_valid_response(self):
        resp = EmergencyResponse(
            job_id="job_emergency_001",
            status="executing",
            eta_minutes=15,
        )
        assert resp.job_id == "job_emergency_001"
        assert resp.status == "executing"
        assert resp.eta_minutes == 15

    def test_default_status(self):
        resp = EmergencyResponse(
            job_id="job_emergency_002",
            eta_minutes=30,
        )
        assert resp.status == "executing"


class TestCancelResponse:
    """Test CancelResponse model."""

    def test_cancelled_response(self):
        resp = CancelResponse(cancelled=True)
        assert resp.cancelled is True
        assert resp.refunded_to_queue is False

    def test_cancelled_with_refund(self):
        resp = CancelResponse(cancelled=True, refunded_to_queue=True)
        assert resp.cancelled is True
        assert resp.refunded_to_queue is True

    def test_not_cancelled(self):
        resp = CancelResponse(cancelled=False)
        assert resp.cancelled is False


class TestSerialization:
    """Test JSON serialization/deserialization."""

    def test_workload_round_trip(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_test",
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
            priority=Priority.NORMAL,
            created_at=now,
        )
        json_str = wl.model_dump_json()
        wl_restored = Workload.model_validate_json(json_str)
        assert wl_restored.id == wl.id
        assert wl_restored.type == wl.type

    def test_scheduled_job_round_trip(self):
        now = datetime.now(timezone.utc)
        wl = Workload(
            id="wl_1",
            agent_id="clinic-001",
            type=WorkloadType.SYNC,
            size_gb=25,
            priority=Priority.URGENT,
            created_at=now,
        )
        job = ScheduledJob(
            id="job_test",
            workloads=[wl],
            window=TimeWindow(start=now, end=now + timedelta(hours=2)),
            estimated_cost=Decimal("8.75"),
            confidence=0.90,
            status=JobStatus.SCHEDULED,
        )
        json_str = job.model_dump_json()
        job_restored = ScheduledJob.model_validate_json(json_str)
        assert job_restored.id == job.id
        assert len(job_restored.workloads) == 1
        assert job_restored.estimated_cost == job.estimated_cost

    def test_scheduler_settings_round_trip(self):
        settings = SchedulerSettings.aggressive()
        json_str = settings.model_dump_json()
        settings_restored = SchedulerSettings.model_validate_json(json_str)
        assert settings_restored.min_confidence == settings.min_confidence
        assert settings_restored.lookahead_hours == settings.lookahead_hours
