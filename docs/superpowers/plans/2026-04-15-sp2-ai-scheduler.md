# SP2: AI Scheduler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the AI Scheduler — SunShift's core intelligence layer that decides **when** to migrate workloads based on TOU pricing forecasts and hurricane alerts using a Hybrid algorithm (Greedy + Lookahead + Batching).

**Architecture:** Hybrid scheduler with three modes: Greedy (for urgent/hurricane), Lookahead (48h optimization), and Batching (efficiency). Integrates with existing ML Engine from SP1 for cost forecasts. Uses probabilistic scoring (`savings × confidence²`) to handle forecast uncertainty.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, existing SP1 ML Engine, pytest

**Spec:** `docs/superpowers/specs/2026-04-15-ai-scheduler-design.md`

---

## File Structure

```
sunshift/backend/
├── models/
│   └── scheduler.py              # NEW: Scheduler-specific Pydantic models
├── services/
│   ├── scheduler_service.py      # NEW: Core scheduling logic (Hybrid algorithm)
│   ├── batching_service.py       # NEW: Batch queue management
│   └── hurricane_shield.py       # EXISTING: Integrate with scheduler
├── api/routes/
│   └── scheduler.py              # NEW: Scheduler REST endpoints
└── tests/
    ├── test_scheduler_models.py  # NEW
    ├── test_scheduler_service.py # NEW
    ├── test_batching_service.py  # NEW
    └── test_scheduler_routes.py  # NEW

sunshift/dashboard/src/components/scheduler/
├── SchedulerCard.tsx             # NEW: Main dashboard card
├── ScheduleTimeline.tsx          # NEW: 48h timeline visualization
├── ModeSelector.tsx              # NEW: Preset mode picker
├── BatchQueueStatus.tsx          # NEW: Queue display
├── hooks/
│   ├── useScheduler.ts           # NEW: API calls + state
│   └── useSchedulePolling.ts     # NEW: Real-time updates
└── index.ts                      # NEW: Barrel export
```

---

### Task 0: Scheduler Pydantic Models

**Goal:** Create all Pydantic models for the scheduler: Workload, ScheduledJob, CostWindow, BatchQueue, and API request/response schemas.

**Files:**
- Create: `sunshift/backend/models/scheduler.py`
- Create: `sunshift/tests/backend/test_scheduler_models.py`

**Acceptance Criteria:**
- [ ] All models from spec are implemented with proper validation
- [ ] Enums for WorkloadType, Priority, JobStatus, RiskLevel
- [ ] Models serialize/deserialize correctly
- [ ] Tests cover valid and invalid inputs

**Verify:** `cd sunshift && uv run pytest tests/backend/test_scheduler_models.py -v`

**Steps:**

- [ ] **Step 1: Write failing tests for scheduler models**

Create `sunshift/tests/backend/test_scheduler_models.py`:

```python
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pydantic import ValidationError

from backend.models.scheduler import (
    WorkloadType, Priority, JobStatus, RiskLevel,
    Workload, TimeWindow, CostWindow, ScheduledJob, BatchQueue,
    WorkloadSubmitRequest, WorkloadSubmitResponse, ScheduleResponse,
    SettingsUpdateRequest, SchedulerSettings, EmergencyRequest, EmergencyResponse,
)


class TestWorkload:
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


class TestCostWindow:
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


class TestScheduledJob:
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


class TestBatchQueue:
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


class TestWorkloadSubmitRequest:
    def test_valid_request(self):
        req = WorkloadSubmitRequest(
            agent_id="clinic-001",
            type=WorkloadType.BACKUP,
            size_gb=50,
        )
        assert req.priority == Priority.NORMAL

    def test_rejects_invalid_type(self):
        with pytest.raises(ValidationError):
            WorkloadSubmitRequest(
                agent_id="clinic-001",
                type="INVALID",
                size_gb=50,
            )


class TestSchedulerSettings:
    def test_balanced_preset(self):
        settings = SchedulerSettings.balanced()
        assert settings.min_confidence == 0.75
        assert settings.lookahead_hours == 48
        assert settings.batch_wait_max_hours == 2

    def test_conservative_preset(self):
        settings = SchedulerSettings.conservative()
        assert settings.min_confidence == 0.90
        assert settings.lookahead_hours == 24

    def test_aggressive_preset(self):
        settings = SchedulerSettings.aggressive()
        assert settings.min_confidence == 0.60
        assert settings.batch_wait_max_hours == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.models.scheduler'`

- [ ] **Step 3: Implement scheduler models**

Create `sunshift/backend/models/scheduler.py`:

```python
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class WorkloadType(str, enum.Enum):
    BACKUP = "BACKUP"
    SYNC = "SYNC"
    AI_TRAIN = "AI_TRAIN"


class Priority(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgent"


class JobStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Workload(BaseModel):
    id: str
    agent_id: str
    type: WorkloadType
    size_gb: int = Field(..., ge=0)
    priority: Priority = Priority.NORMAL
    deadline: datetime | None = None
    created_at: datetime


class TimeWindow(BaseModel):
    start: datetime
    end: datetime


class CostWindow(BaseModel):
    start: datetime
    end: datetime
    avg_cost_cents_kwh: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    score: float = Field(default=0)
    weather_risk: RiskLevel = RiskLevel.LOW


class ScheduledJob(BaseModel):
    id: str
    workloads: list[Workload]
    window: TimeWindow
    estimated_cost: Decimal = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    status: JobStatus = JobStatus.SCHEDULED


class BatchQueue(BaseModel):
    workloads: list[Workload] = Field(default_factory=list)
    total_size_gb: int = Field(default=0, ge=0)
    oldest_arrival: datetime | None = None
    target_window: CostWindow | None = None
    flush_at: datetime | None = None


class BatchQueueStatus(BaseModel):
    count: int = 0
    total_size_gb: int = 0
    oldest_arrival: datetime | None = None
    flush_at: datetime | None = None
    target_window_start: datetime | None = None


# API Request/Response Models

class WorkloadSubmitRequest(BaseModel):
    agent_id: str
    type: WorkloadType
    size_gb: int = Field(..., ge=1)
    priority: Priority = Priority.NORMAL
    deadline: datetime | None = None


class WorkloadSubmitResponse(BaseModel):
    workload_id: str
    scheduled_window: TimeWindow | None = None
    batch_queue_position: int | None = None
    estimated_savings: Decimal


class HourlyCost(BaseModel):
    hour: datetime
    cost_cents_kwh: float
    confidence: float


class ScheduleResponse(BaseModel):
    jobs: list[ScheduledJob]
    next_window: CostWindow | None = None
    batch_queue_status: BatchQueueStatus
    cost_forecast: list[HourlyCost]


class SchedulerSettings(BaseModel):
    min_confidence: float = Field(default=0.75, ge=0, le=1)
    lookahead_hours: int = Field(default=48, ge=1, le=168)
    batch_wait_max_hours: int = Field(default=2, ge=1, le=12)
    replan_frequency_hours: int = Field(default=6, ge=1, le=24)
    hurricane_trigger_level: str = Field(default="warning")

    @classmethod
    def conservative(cls) -> SchedulerSettings:
        return cls(
            min_confidence=0.90,
            lookahead_hours=24,
            batch_wait_max_hours=1,
            replan_frequency_hours=2,
            hurricane_trigger_level="watch",
        )

    @classmethod
    def balanced(cls) -> SchedulerSettings:
        return cls(
            min_confidence=0.75,
            lookahead_hours=48,
            batch_wait_max_hours=2,
            replan_frequency_hours=6,
            hurricane_trigger_level="warning",
        )

    @classmethod
    def aggressive(cls) -> SchedulerSettings:
        return cls(
            min_confidence=0.60,
            lookahead_hours=48,
            batch_wait_max_hours=4,
            replan_frequency_hours=12,
            hurricane_trigger_level="warning",
        )


class SettingsUpdateRequest(BaseModel):
    mode: str = Field(..., pattern=r"^(conservative|balanced|aggressive)$")


class SettingsUpdateResponse(BaseModel):
    mode: str
    effective_settings: SchedulerSettings


class EmergencyRequest(BaseModel):
    agent_id: str
    reason: str = Field(..., pattern=r"^(hurricane|manual)$")


class EmergencyResponse(BaseModel):
    job_id: str
    status: str = "executing"
    eta_minutes: int


class CancelResponse(BaseModel):
    cancelled: bool
    refunded_to_queue: bool = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_models.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/models/scheduler.py sunshift/tests/backend/test_scheduler_models.py
git commit -m "feat(sp2): scheduler Pydantic models — Workload, ScheduledJob, CostWindow, BatchQueue"
```

---

### Task 1: Window Scoring Service

**Goal:** Implement the probabilistic window scoring formula: `score = (peak_cost - window_cost) × confidence² × duration_hours`

**Files:**
- Create: `sunshift/backend/services/window_scoring.py`
- Create: `sunshift/tests/backend/test_window_scoring.py`

**Acceptance Criteria:**
- [ ] Scoring formula matches spec exactly
- [ ] Low confidence reduces score quadratically
- [ ] Longer windows get higher scores (more savings potential)
- [ ] Windows are ranked correctly by score

**Verify:** `cd sunshift && uv run pytest tests/backend/test_window_scoring.py -v`

**Steps:**

- [ ] **Step 1: Write failing tests**

Create `sunshift/tests/backend/test_window_scoring.py`:

```python
import pytest
from datetime import datetime, timezone, timedelta

from backend.services.window_scoring import WindowScorer, ScoredWindow
from backend.models.scheduler import CostWindow, RiskLevel


class TestWindowScorer:
    @pytest.fixture
    def scorer(self):
        return WindowScorer(peak_cost_cents=25.0)

    def test_score_formula_correct(self, scorer):
        """Verify: score = (peak - window) × conf² × hours"""
        now = datetime.now(timezone.utc)
        window = CostWindow(
            start=now,
            end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        scored = scorer.score_window(window)
        # (25 - 8) × 0.85² × 4 = 17 × 0.7225 × 4 = 49.13
        assert abs(scored.score - 49.13) < 0.1

    def test_low_confidence_reduces_score(self, scorer):
        """Low confidence should significantly reduce score due to confidence²"""
        now = datetime.now(timezone.utc)
        high_conf = CostWindow(
            start=now, end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0, confidence=0.90, weather_risk=RiskLevel.LOW,
        )
        low_conf = CostWindow(
            start=now, end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0, confidence=0.60, weather_risk=RiskLevel.LOW,
        )
        high_scored = scorer.score_window(high_conf)
        low_scored = scorer.score_window(low_conf)
        # 0.90² / 0.60² = 0.81 / 0.36 = 2.25x difference
        assert high_scored.score > low_scored.score * 2

    def test_longer_window_higher_score(self, scorer):
        """Same cost, longer duration = higher score"""
        now = datetime.now(timezone.utc)
        short = CostWindow(
            start=now, end=now + timedelta(hours=2),
            avg_cost_cents_kwh=8.0, confidence=0.85, weather_risk=RiskLevel.LOW,
        )
        long = CostWindow(
            start=now, end=now + timedelta(hours=6),
            avg_cost_cents_kwh=8.0, confidence=0.85, weather_risk=RiskLevel.LOW,
        )
        short_scored = scorer.score_window(short)
        long_scored = scorer.score_window(long)
        assert long_scored.score > short_scored.score

    def test_ranks_windows_correctly(self, scorer):
        """Best score gets rank 1"""
        now = datetime.now(timezone.utc)
        windows = [
            CostWindow(start=now, end=now + timedelta(hours=4), avg_cost_cents_kwh=15.0, confidence=0.80, weather_risk=RiskLevel.LOW),
            CostWindow(start=now + timedelta(hours=4), end=now + timedelta(hours=8), avg_cost_cents_kwh=8.0, confidence=0.90, weather_risk=RiskLevel.LOW),
            CostWindow(start=now + timedelta(hours=8), end=now + timedelta(hours=12), avg_cost_cents_kwh=10.0, confidence=0.85, weather_risk=RiskLevel.LOW),
        ]
        ranked = scorer.rank_windows(windows, top_n=3)
        assert ranked[0].rank == 1
        assert ranked[0].score > ranked[1].score
        assert ranked[1].score > ranked[2].score
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd sunshift && uv run pytest tests/backend/test_window_scoring.py -v`
Expected: FAIL

- [ ] **Step 3: Implement window scoring**

Create `sunshift/backend/services/window_scoring.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.models.scheduler import CostWindow


@dataclass
class ScoredWindow:
    window: CostWindow
    score: float
    rank: int = 0
    estimated_savings_dollars: float = 0.0


class WindowScorer:
    """
    Scores cost windows using probabilistic formula:
    score = (peak_cost - window_cost) × confidence² × duration_hours

    The confidence² term penalizes uncertain forecasts quadratically,
    preferring reliable windows over potentially better but uncertain ones.
    """

    def __init__(self, peak_cost_cents: float = 25.0, kwh_per_hour: float = 2.5):
        self.peak_cost_cents = peak_cost_cents
        self.kwh_per_hour = kwh_per_hour  # Estimated workload power consumption

    def score_window(self, window: CostWindow) -> ScoredWindow:
        duration_hours = (window.end - window.start).total_seconds() / 3600
        savings_per_hour = self.peak_cost_cents - window.avg_cost_cents_kwh
        confidence_factor = window.confidence ** 2

        score = savings_per_hour * confidence_factor * duration_hours

        # Estimate dollar savings
        estimated_kwh = self.kwh_per_hour * duration_hours
        savings_dollars = (savings_per_hour / 100) * estimated_kwh

        return ScoredWindow(
            window=window,
            score=round(score, 2),
            estimated_savings_dollars=round(max(0, savings_dollars), 2),
        )

    def rank_windows(self, windows: list[CostWindow], top_n: int = 3) -> list[ScoredWindow]:
        scored = [self.score_window(w) for w in windows]
        scored.sort(key=lambda sw: sw.score, reverse=True)

        for rank, sw in enumerate(scored[:top_n], 1):
            sw.rank = rank

        return scored[:top_n]
```

- [ ] **Step 4: Run tests**

Run: `cd sunshift && uv run pytest tests/backend/test_window_scoring.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/services/window_scoring.py sunshift/tests/backend/test_window_scoring.py
git commit -m "feat(sp2): window scoring — probabilistic formula (savings × confidence²)"
```

---

### Task 2: Batching Service

**Goal:** Implement batch queue management: add workloads, check flush conditions, create batch jobs.

**Files:**
- Create: `sunshift/backend/services/batching_service.py`
- Create: `sunshift/tests/backend/test_batching_service.py`

**Acceptance Criteria:**
- [ ] Small workloads (<50GB) are added to queue
- [ ] Queue flushes when: 2+ jobs OR 2h max wait
- [ ] Large workloads (≥50GB) bypass queue
- [ ] Urgent workloads bypass queue
- [ ] Batch job combines multiple workloads

**Verify:** `cd sunshift && uv run pytest tests/backend/test_batching_service.py -v`

**Steps:**

- [ ] **Step 1: Write failing tests**

Create `sunshift/tests/backend/test_batching_service.py`:

```python
import pytest
from datetime import datetime, timezone, timedelta

from backend.services.batching_service import BatchingService
from backend.models.scheduler import Workload, WorkloadType, Priority, SchedulerSettings


def make_workload(
    id: str = "wl_1",
    size_gb: int = 25,
    priority: Priority = Priority.NORMAL,
    created_at: datetime | None = None,
) -> Workload:
    return Workload(
        id=id,
        agent_id="clinic-001",
        type=WorkloadType.BACKUP,
        size_gb=size_gb,
        priority=priority,
        created_at=created_at or datetime.now(timezone.utc),
    )


class TestBatchingService:
    @pytest.fixture
    def service(self):
        settings = SchedulerSettings.balanced()
        return BatchingService(settings)

    def test_adds_small_workload_to_queue(self, service):
        wl = make_workload(size_gb=25)
        status = service.add_to_queue(wl)
        assert status.count == 1
        assert status.total_size_gb == 25

    def test_flushes_when_min_jobs_reached(self, service):
        wl1 = make_workload(id="wl_1", size_gb=20)
        wl2 = make_workload(id="wl_2", size_gb=25)
        service.add_to_queue(wl1)
        service.add_to_queue(wl2)
        should_flush, reason = service.should_flush()
        assert should_flush is True
        assert "min_jobs" in reason

    def test_flushes_after_2h_wait(self, service):
        old_time = datetime.now(timezone.utc) - timedelta(hours=2, minutes=1)
        wl = make_workload(created_at=old_time)
        service.add_to_queue(wl)
        should_flush, reason = service.should_flush()
        assert should_flush is True
        assert "max_wait" in reason

    def test_large_workload_bypasses_queue(self, service):
        wl = make_workload(size_gb=60)
        bypasses = service.should_bypass(wl)
        assert bypasses is True

    def test_urgent_workload_bypasses_queue(self, service):
        wl = make_workload(size_gb=25, priority=Priority.URGENT)
        bypasses = service.should_bypass(wl)
        assert bypasses is True

    def test_create_batch_job_combines_workloads(self, service):
        wl1 = make_workload(id="wl_1", size_gb=20)
        wl2 = make_workload(id="wl_2", size_gb=25)
        service.add_to_queue(wl1)
        service.add_to_queue(wl2)

        from backend.models.scheduler import CostWindow, RiskLevel
        target = CostWindow(
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc) + timedelta(hours=4),
            avg_cost_cents_kwh=8.0,
            confidence=0.85,
            weather_risk=RiskLevel.LOW,
        )
        job = service.create_batch_job(target)
        assert len(job.workloads) == 2
        assert job.status.value == "scheduled"

    def test_cleanup_clears_queue(self, service):
        wl = make_workload()
        service.add_to_queue(wl)
        count = service.cleanup()
        assert count == 1
        assert service.get_status().count == 0
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd sunshift && uv run pytest tests/backend/test_batching_service.py -v`
Expected: FAIL

- [ ] **Step 3: Implement batching service**

Create `sunshift/backend/services/batching_service.py`:

```python
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from backend.models.scheduler import (
    Workload, ScheduledJob, CostWindow, BatchQueue, BatchQueueStatus,
    TimeWindow, JobStatus, Priority, SchedulerSettings,
)


class BatchingService:
    """
    Manages the batch queue for workload aggregation.

    Rules (from spec):
    - Min jobs to flush: 2
    - Max wait time: 2 hours (configurable via settings)
    - Max batch size: 200 GB
    - Bypass threshold: 50 GB (large jobs run solo)
    """

    BYPASS_THRESHOLD_GB = 50
    MAX_BATCH_SIZE_GB = 200
    MIN_JOBS_TO_FLUSH = 2

    def __init__(self, settings: SchedulerSettings):
        self.settings = settings
        self._queue = BatchQueue()

    def add_to_queue(self, workload: Workload) -> BatchQueueStatus:
        self._queue.workloads.append(workload)
        self._queue.total_size_gb += workload.size_gb

        if self._queue.oldest_arrival is None:
            self._queue.oldest_arrival = workload.created_at
            self._queue.flush_at = workload.created_at + timedelta(
                hours=self.settings.batch_wait_max_hours
            )

        return self.get_status()

    def should_bypass(self, workload: Workload) -> bool:
        """Large or urgent workloads bypass the queue."""
        if workload.size_gb >= self.BYPASS_THRESHOLD_GB:
            return True
        if workload.priority == Priority.URGENT:
            return True
        if workload.deadline is not None:
            # Has explicit deadline — schedule immediately
            return True
        return False

    def should_flush(self) -> tuple[bool, str]:
        """Check if queue should be flushed."""
        if len(self._queue.workloads) == 0:
            return False, ""

        # Condition 1: Minimum jobs reached
        if len(self._queue.workloads) >= self.MIN_JOBS_TO_FLUSH:
            return True, "min_jobs_reached"

        # Condition 2: Max wait time exceeded
        if self._queue.oldest_arrival:
            now = datetime.now(timezone.utc)
            max_wait = timedelta(hours=self.settings.batch_wait_max_hours)
            if now - self._queue.oldest_arrival >= max_wait:
                return True, "max_wait_exceeded"

        # Condition 3: Max batch size reached
        if self._queue.total_size_gb >= self.MAX_BATCH_SIZE_GB:
            return True, "max_size_reached"

        return False, ""

    def create_batch_job(self, target_window: CostWindow) -> ScheduledJob:
        """Create a scheduled job from all queued workloads."""
        job = ScheduledJob(
            id=f"job_{uuid.uuid4().hex[:12]}",
            workloads=list(self._queue.workloads),
            window=TimeWindow(start=target_window.start, end=target_window.end),
            estimated_cost=Decimal("0"),  # Will be calculated by scheduler
            confidence=target_window.confidence,
            status=JobStatus.SCHEDULED,
        )

        # Clear the queue
        self._queue = BatchQueue()

        return job

    def get_status(self) -> BatchQueueStatus:
        return BatchQueueStatus(
            count=len(self._queue.workloads),
            total_size_gb=self._queue.total_size_gb,
            oldest_arrival=self._queue.oldest_arrival,
            flush_at=self._queue.flush_at,
            target_window_start=self._queue.target_window.start if self._queue.target_window else None,
        )

    def cleanup(self) -> int:
        """Clear stale batches. Returns count of cleaned workloads."""
        count = len(self._queue.workloads)
        self._queue = BatchQueue()
        return count

    def get_queue(self) -> BatchQueue:
        return self._queue
```

- [ ] **Step 4: Run tests**

Run: `cd sunshift && uv run pytest tests/backend/test_batching_service.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/services/batching_service.py sunshift/tests/backend/test_batching_service.py
git commit -m "feat(sp2): batching service — queue management, flush conditions, batch job creation"
```

---

### Task 3: Scheduler Service (Core Algorithm)

**Goal:** Implement the Hybrid scheduler with Greedy, Lookahead, and Batching modes following the decision flow from spec.

**Files:**
- Create: `sunshift/backend/services/scheduler_service.py`
- Create: `sunshift/tests/backend/test_scheduler_service.py`

**Acceptance Criteria:**
- [ ] Hurricane alert triggers Greedy mode (execute NOW)
- [ ] Urgent workloads use Greedy mode (6h horizon)
- [ ] Flexible workloads use Lookahead mode (48h horizon)
- [ ] Small workloads are batched, large run solo
- [ ] Replan updates scheduled jobs when forecast changes

**Verify:** `cd sunshift && uv run pytest tests/backend/test_scheduler_service.py -v`

**Steps:**

- [ ] **Step 1: Write failing tests**

Create `sunshift/tests/backend/test_scheduler_service.py`:

```python
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from backend.services.scheduler_service import SchedulerService, ScheduleMode
from backend.models.scheduler import Workload, WorkloadType, Priority, SchedulerSettings, CostWindow, RiskLevel
from backend.services.hurricane_shield import ThreatLevel, ShieldStatus


def make_workload(
    id: str = "wl_1",
    size_gb: int = 25,
    priority: Priority = Priority.NORMAL,
    deadline: datetime | None = None,
) -> Workload:
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
    """Generate mock cost windows with realistic TOU pattern."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    windows = []
    for i in range(count):
        hour = (now.hour + i) % 24
        # FPL TOU: Peak 12-21, Off-peak otherwise
        if 12 <= hour < 21:
            cost = 23.0 + (i % 5)  # Peak
            conf = 0.75
        elif 6 <= hour < 12:
            cost = 12.0 + (i % 3)  # Shoulder
            conf = 0.85
        else:
            cost = 6.0 + (i % 2)  # Off-peak
            conf = 0.92

        windows.append(CostWindow(
            start=now + timedelta(hours=i),
            end=now + timedelta(hours=i + 1),
            avg_cost_cents_kwh=cost,
            confidence=conf,
            weather_risk=RiskLevel.LOW,
        ))
    return windows


class TestSchedulerService:
    @pytest.fixture
    def service(self):
        settings = SchedulerSettings.balanced()
        return SchedulerService(settings)

    def test_greedy_selects_next_cheap_slot(self, service):
        """Greedy mode should pick the cheapest slot within 6h."""
        windows = make_cost_windows(12)
        mode = service._determine_mode(make_workload(priority=Priority.URGENT), hurricane_active=False)
        assert mode == ScheduleMode.GREEDY

        best = service._find_best_window_greedy(windows[:6])
        # Should be one of the low-cost windows
        assert best.avg_cost_cents_kwh < 15.0

    def test_lookahead_finds_optimal_48h_window(self, service):
        """Lookahead mode should find best window in 48h."""
        windows = make_cost_windows(48)
        mode = service._determine_mode(make_workload(), hurricane_active=False)
        assert mode == ScheduleMode.LOOKAHEAD

        best = service._find_best_window_lookahead(windows)
        # Off-peak windows should be selected
        assert best.avg_cost_cents_kwh < 10.0

    def test_hurricane_triggers_greedy_override(self, service):
        """Hurricane alert should force Greedy mode regardless of workload."""
        wl = make_workload(priority=Priority.NORMAL)
        mode = service._determine_mode(wl, hurricane_active=True)
        assert mode == ScheduleMode.GREEDY

    def test_confidence_scoring_weights_correctly(self, service):
        """Higher confidence windows should be preferred."""
        now = datetime.now(timezone.utc)
        high_conf = CostWindow(
            start=now, end=now + timedelta(hours=4),
            avg_cost_cents_kwh=8.0, confidence=0.90, weather_risk=RiskLevel.LOW,
        )
        low_conf = CostWindow(
            start=now, end=now + timedelta(hours=4),
            avg_cost_cents_kwh=7.0, confidence=0.50, weather_risk=RiskLevel.LOW,
        )
        # Even though low_conf has lower cost, high_conf should score better
        high_score = service._score_window(high_conf)
        low_score = service._score_window(low_conf)
        assert high_score > low_score

    async def test_schedule_workload_returns_job(self, service):
        """schedule_workload should return a ScheduledJob."""
        wl = make_workload(size_gb=60)  # Large, bypasses batching
        windows = make_cost_windows(48)

        with patch.object(service, '_get_cost_windows', return_value=windows):
            with patch.object(service, '_is_hurricane_active', return_value=False):
                job = await service.schedule_workload(wl)
                assert job is not None
                assert len(job.workloads) == 1
                assert job.workloads[0].id == "wl_1"


class TestScheduleMode:
    def test_mode_enum_values(self):
        assert ScheduleMode.GREEDY.value == "greedy"
        assert ScheduleMode.LOOKAHEAD.value == "lookahead"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_service.py -v`
Expected: FAIL

- [ ] **Step 3: Implement scheduler service**

Create `sunshift/backend/services/scheduler_service.py`:

```python
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from backend.models.scheduler import (
    Workload, ScheduledJob, CostWindow, TimeWindow,
    JobStatus, Priority, SchedulerSettings, RiskLevel,
)
from backend.services.batching_service import BatchingService
from backend.services.window_scoring import WindowScorer
from backend.services.hurricane_shield import ShieldOrchestrator, ThreatLevel


class ScheduleMode(str, enum.Enum):
    GREEDY = "greedy"      # Next available window, used for urgent/hurricane
    LOOKAHEAD = "lookahead"  # Best window in 48h horizon


class SchedulerService:
    """
    Hybrid scheduler implementing the decision flow from spec:

    1. Hurricane active? → GREEDY (execute NOW)
    2. Urgent/deadline? → GREEDY (best in 6h)
    3. Flexible? → LOOKAHEAD (best in 48h)
    4. Batchable (<50GB)? → Add to batch queue
    5. Large (≥50GB)? → Schedule solo
    """

    GREEDY_HORIZON_HOURS = 6
    LOOKAHEAD_HORIZON_HOURS = 48

    def __init__(self, settings: SchedulerSettings):
        self.settings = settings
        self.batching = BatchingService(settings)
        self.scorer = WindowScorer()
        self.shield = ShieldOrchestrator()
        self._scheduled_jobs: dict[str, ScheduledJob] = {}

    def _determine_mode(self, workload: Workload, hurricane_active: bool) -> ScheduleMode:
        """Determine scheduling mode based on conditions."""
        if hurricane_active:
            return ScheduleMode.GREEDY
        if workload.priority == Priority.URGENT:
            return ScheduleMode.GREEDY
        if workload.deadline is not None:
            return ScheduleMode.GREEDY
        return ScheduleMode.LOOKAHEAD

    def _score_window(self, window: CostWindow) -> float:
        """Score a window using probabilistic formula."""
        return self.scorer.score_window(window).score

    def _find_best_window_greedy(self, windows: list[CostWindow]) -> CostWindow:
        """Find best window within greedy horizon (6h)."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=self.GREEDY_HORIZON_HOURS)
        candidates = [w for w in windows if w.start <= cutoff]
        if not candidates:
            candidates = windows[:self.GREEDY_HORIZON_HOURS]

        return max(candidates, key=self._score_window)

    def _find_best_window_lookahead(self, windows: list[CostWindow]) -> CostWindow:
        """Find best window within lookahead horizon (48h)."""
        horizon = self.settings.lookahead_hours
        candidates = windows[:horizon]

        # Filter by minimum confidence
        filtered = [w for w in candidates if w.confidence >= self.settings.min_confidence]
        if not filtered:
            filtered = candidates

        return max(filtered, key=self._score_window)

    def _get_cost_windows(self) -> list[CostWindow]:
        """Get cost forecast from ML Engine. Stub for now."""
        # TODO: Integrate with ML Engine from SP1
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        windows = []
        for i in range(48):
            hour = (now.hour + i) % 24
            if 12 <= hour < 21:
                cost = 23.0
                conf = 0.75
            elif 6 <= hour < 12:
                cost = 12.0
                conf = 0.85
            else:
                cost = 6.0
                conf = 0.92

            windows.append(CostWindow(
                start=now + timedelta(hours=i),
                end=now + timedelta(hours=i + 1),
                avg_cost_cents_kwh=cost,
                confidence=conf,
                weather_risk=RiskLevel.LOW,
            ))
        return windows

    def _is_hurricane_active(self) -> bool:
        """Check if hurricane shield is active."""
        return self.shield.status.shield_mode == "active"

    async def schedule_workload(self, workload: Workload) -> ScheduledJob | None:
        """
        Main scheduling entry point.

        Returns ScheduledJob if scheduled immediately, None if batched.
        """
        hurricane_active = self._is_hurricane_active()
        mode = self._determine_mode(workload, hurricane_active)
        windows = self._get_cost_windows()

        # Check if workload should bypass batching
        if not self.batching.should_bypass(workload):
            # Add to batch queue
            self.batching.add_to_queue(workload)

            # Check if we should flush
            should_flush, _ = self.batching.should_flush()
            if should_flush:
                target = self._find_best_window_lookahead(windows)
                job = self.batching.create_batch_job(target)
                self._scheduled_jobs[job.id] = job
                return job

            return None  # Workload is queued

        # Schedule immediately (large or urgent)
        if mode == ScheduleMode.GREEDY:
            target = self._find_best_window_greedy(windows)
        else:
            target = self._find_best_window_lookahead(windows)

        job = ScheduledJob(
            id=f"job_{uuid.uuid4().hex[:12]}",
            workloads=[workload],
            window=TimeWindow(start=target.start, end=target.end),
            estimated_cost=Decimal("0"),
            confidence=target.confidence,
            status=JobStatus.SCHEDULED,
        )
        self._scheduled_jobs[job.id] = job
        return job

    def find_optimal_windows(self, horizon_hours: int = 48) -> list[CostWindow]:
        """Find optimal windows in the given horizon."""
        windows = self._get_cost_windows()[:horizon_hours]
        ranked = self.scorer.rank_windows(windows, top_n=5)
        return [sw.window for sw in ranked]

    def get_scheduled_jobs(self, agent_id: str | None = None) -> list[ScheduledJob]:
        """Get all scheduled jobs, optionally filtered by agent."""
        jobs = list(self._scheduled_jobs.values())
        if agent_id:
            jobs = [j for j in jobs if any(w.agent_id == agent_id for w in j.workloads)]
        return jobs

    async def trigger_emergency(self, agent_id: str, reason: str) -> ScheduledJob:
        """Trigger emergency backup for hurricane or manual override."""
        # Create immediate job for all pending workloads
        pending = [w for w in self.batching.get_queue().workloads if w.agent_id == agent_id]
        if not pending:
            # Create placeholder workload for emergency
            pending = [Workload(
                id=f"wl_emergency_{uuid.uuid4().hex[:8]}",
                agent_id=agent_id,
                type="BACKUP",
                size_gb=0,
                priority=Priority.URGENT,
                created_at=datetime.now(timezone.utc),
            )]

        now = datetime.now(timezone.utc)
        job = ScheduledJob(
            id=f"job_emergency_{uuid.uuid4().hex[:8]}",
            workloads=pending,
            window=TimeWindow(start=now, end=now + timedelta(hours=4)),
            estimated_cost=Decimal("0"),
            confidence=1.0,
            status=JobStatus.RUNNING,
        )
        self._scheduled_jobs[job.id] = job
        return job

    async def replan_on_forecast_update(self) -> list[ScheduledJob]:
        """Replan scheduled jobs when forecast updates."""
        windows = self._get_cost_windows()
        updated = []

        for job_id, job in self._scheduled_jobs.items():
            if job.status != JobStatus.SCHEDULED:
                continue

            # Find new best window
            best = self._find_best_window_lookahead(windows)

            # Only reschedule if significantly better (>10% improvement)
            current_score = self._score_window(CostWindow(
                start=job.window.start,
                end=job.window.end,
                avg_cost_cents_kwh=15.0,  # Estimated
                confidence=job.confidence,
                weather_risk=RiskLevel.LOW,
            ))
            new_score = self._score_window(best)

            if new_score > current_score * 1.1:
                job.window = TimeWindow(start=best.start, end=best.end)
                job.confidence = best.confidence
                updated.append(job)

        return updated
```

- [ ] **Step 4: Run tests**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_service.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/services/scheduler_service.py sunshift/tests/backend/test_scheduler_service.py
git commit -m "feat(sp2): scheduler service — Hybrid algorithm (Greedy + Lookahead + Batching)"
```

---

### Task 4: Scheduler API Routes

**Goal:** Implement REST API endpoints for the scheduler.

**Files:**
- Create: `sunshift/backend/api/routes/scheduler.py`
- Modify: `sunshift/backend/main.py` (add router)
- Create: `sunshift/tests/backend/test_scheduler_routes.py`

**Acceptance Criteria:**
- [ ] POST /api/v1/scheduler/workloads — submit workload
- [ ] GET /api/v1/scheduler/schedule — get schedule for agent
- [ ] PUT /api/v1/scheduler/settings — update preset mode
- [ ] POST /api/v1/scheduler/emergency — trigger emergency
- [ ] DELETE /api/v1/scheduler/workloads/{id} — cancel workload

**Verify:** `cd sunshift && uv run pytest tests/backend/test_scheduler_routes.py -v`

**Steps:**

- [ ] **Step 1: Write failing tests**

Create `sunshift/tests/backend/test_scheduler_routes.py`:

```python
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestSchedulerWorkloads:
    async def test_submit_workload(self, client):
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "BACKUP",
            "size_gb": 50,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "workload_id" in data
        assert "estimated_savings" in data

    async def test_submit_urgent_workload_schedules_immediately(self, client):
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "BACKUP",
            "size_gb": 60,
            "priority": "urgent",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scheduled_window"] is not None

    async def test_submit_small_workload_batches(self, client):
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "SYNC",
            "size_gb": 20,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["batch_queue_position"] is not None


class TestSchedulerSchedule:
    async def test_get_schedule(self, client):
        resp = await client.get("/api/v1/scheduler/schedule", params={"agent_id": "clinic-001"})
        assert resp.status_code == 200
        data = resp.json()
        assert "jobs" in data
        assert "batch_queue_status" in data
        assert "cost_forecast" in data


class TestSchedulerSettings:
    async def test_update_mode_to_aggressive(self, client):
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "aggressive"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "aggressive"
        assert data["effective_settings"]["min_confidence"] == 0.60

    async def test_invalid_mode_returns_422(self, client):
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "invalid"})
        assert resp.status_code == 422


class TestSchedulerEmergency:
    async def test_trigger_emergency(self, client):
        resp = await client.post("/api/v1/scheduler/emergency", json={
            "agent_id": "clinic-001",
            "reason": "hurricane",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "executing"
        assert "job_id" in data
        assert "eta_minutes" in data
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_routes.py -v`
Expected: FAIL

- [ ] **Step 3: Implement scheduler routes**

Create `sunshift/backend/api/routes/scheduler.py`:

```python
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException

from backend.models.scheduler import (
    WorkloadSubmitRequest, WorkloadSubmitResponse,
    ScheduleResponse, SettingsUpdateRequest, SettingsUpdateResponse,
    EmergencyRequest, EmergencyResponse, CancelResponse,
    SchedulerSettings, Workload, WorkloadType, Priority,
    BatchQueueStatus, HourlyCost, CostWindow, RiskLevel,
)
from backend.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler")

# In-memory service instance (replace with DI in production)
_settings = SchedulerSettings.balanced()
_service = SchedulerService(_settings)
_workload_counter = 0


@router.post("/workloads", status_code=201, response_model=WorkloadSubmitResponse)
async def submit_workload(request: WorkloadSubmitRequest):
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
        return WorkloadSubmitResponse(
            workload_id=workload.id,
            scheduled_window=job.window,
            batch_queue_position=None,
            estimated_savings=Decimal("4.20"),  # TODO: Calculate from scorer
        )
    else:
        status = _service.batching.get_status()
        return WorkloadSubmitResponse(
            workload_id=workload.id,
            scheduled_window=None,
            batch_queue_position=status.count,
            estimated_savings=Decimal("4.20"),
        )


@router.get("/schedule", response_model=ScheduleResponse)
async def get_schedule(agent_id: str):
    jobs = _service.get_scheduled_jobs(agent_id)
    batch_status = _service.batching.get_status()
    windows = _service.find_optimal_windows(48)

    # Generate cost forecast
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    cost_forecast = []
    for i, w in enumerate(windows):
        cost_forecast.append(HourlyCost(
            hour=w.start,
            cost_cents_kwh=w.avg_cost_cents_kwh,
            confidence=w.confidence,
        ))

    return ScheduleResponse(
        jobs=jobs,
        next_window=windows[0] if windows else None,
        batch_queue_status=batch_status,
        cost_forecast=cost_forecast[:48],
    )


@router.put("/settings", response_model=SettingsUpdateResponse)
async def update_settings(request: SettingsUpdateRequest):
    global _settings, _service

    if request.mode == "conservative":
        _settings = SchedulerSettings.conservative()
    elif request.mode == "balanced":
        _settings = SchedulerSettings.balanced()
    elif request.mode == "aggressive":
        _settings = SchedulerSettings.aggressive()
    else:
        raise HTTPException(status_code=422, detail="Invalid mode")

    _service = SchedulerService(_settings)

    return SettingsUpdateResponse(
        mode=request.mode,
        effective_settings=_settings,
    )


@router.post("/emergency", response_model=EmergencyResponse)
async def trigger_emergency(request: EmergencyRequest):
    job = await _service.trigger_emergency(request.agent_id, request.reason)

    return EmergencyResponse(
        job_id=job.id,
        status="executing",
        eta_minutes=15,  # Estimated
    )


@router.delete("/workloads/{workload_id}", response_model=CancelResponse)
async def cancel_workload(workload_id: str):
    # Find and remove workload from queue or scheduled jobs
    queue = _service.batching.get_queue()
    for i, wl in enumerate(queue.workloads):
        if wl.id == workload_id:
            queue.workloads.pop(i)
            return CancelResponse(cancelled=True, refunded_to_queue=False)

    # Not found in queue, check scheduled jobs
    for job_id, job in _service._scheduled_jobs.items():
        for wl in job.workloads:
            if wl.id == workload_id:
                # Can't cancel from scheduled job in MVP
                raise HTTPException(status_code=400, detail="Cannot cancel scheduled workload")

    raise HTTPException(status_code=404, detail="Workload not found")
```

- [ ] **Step 4: Update main.py to include scheduler router**

Modify `sunshift/backend/main.py`:

```python
from fastapi import FastAPI
from backend.api.routes import agents, predictions, metrics, commands, scheduler
from backend.api.routes.hurricane import router as hurricane_router
from backend.api.websocket import router as ws_router

app = FastAPI(title="SunShift API", version="0.1.0")

app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(commands.router, prefix="/api/v1", tags=["commands"])
app.include_router(scheduler.router, prefix="/api/v1", tags=["scheduler"])
app.include_router(hurricane_router, prefix="/api/v1", tags=["hurricane"])
app.include_router(ws_router, tags=["websocket"])


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests**

Run: `cd sunshift && uv run pytest tests/backend/test_scheduler_routes.py -v`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add sunshift/backend/api/routes/scheduler.py sunshift/backend/main.py sunshift/tests/backend/test_scheduler_routes.py
git commit -m "feat(sp2): scheduler REST API — workloads, schedule, settings, emergency endpoints"
```

---

### Task 5: Dashboard Components — useScheduler Hook

**Goal:** Create React hooks for scheduler API calls and state management.

**Files:**
- Create: `sunshift/dashboard/src/components/scheduler/hooks/useScheduler.ts`
- Create: `sunshift/dashboard/src/components/scheduler/hooks/useSchedulePolling.ts`
- Create: `sunshift/dashboard/src/components/scheduler/index.ts`

**Acceptance Criteria:**
- [ ] useScheduler hook fetches schedule data
- [ ] useSchedulePolling polls every 30s for real-time updates
- [ ] Proper error handling and loading states
- [ ] TypeScript types match backend models

**Steps:**

- [ ] **Step 1: Create TypeScript types**

Create `sunshift/dashboard/src/components/scheduler/types.ts`:

```typescript
export type WorkloadType = 'BACKUP' | 'SYNC' | 'AI_TRAIN';
export type Priority = 'normal' | 'urgent';
export type JobStatus = 'scheduled' | 'running' | 'completed' | 'failed';
export type SchedulerMode = 'conservative' | 'balanced' | 'aggressive';

export interface TimeWindow {
  start: string;
  end: string;
}

export interface Workload {
  id: string;
  agent_id: string;
  type: WorkloadType;
  size_gb: number;
  priority: Priority;
  deadline: string | null;
  created_at: string;
}

export interface ScheduledJob {
  id: string;
  workloads: Workload[];
  window: TimeWindow;
  estimated_cost: string;
  confidence: number;
  status: JobStatus;
}

export interface BatchQueueStatus {
  count: number;
  total_size_gb: number;
  oldest_arrival: string | null;
  flush_at: string | null;
  target_window_start: string | null;
}

export interface HourlyCost {
  hour: string;
  cost_cents_kwh: number;
  confidence: number;
}

export interface CostWindow {
  start: string;
  end: string;
  avg_cost_cents_kwh: number;
  confidence: number;
  score: number;
  weather_risk: 'low' | 'medium' | 'high';
}

export interface ScheduleResponse {
  jobs: ScheduledJob[];
  next_window: CostWindow | null;
  batch_queue_status: BatchQueueStatus;
  cost_forecast: HourlyCost[];
}

export interface SchedulerSettings {
  min_confidence: number;
  lookahead_hours: number;
  batch_wait_max_hours: number;
  replan_frequency_hours: number;
  hurricane_trigger_level: string;
}
```

- [ ] **Step 2: Create useScheduler hook**

Create `sunshift/dashboard/src/components/scheduler/hooks/useScheduler.ts`:

```typescript
import { useState, useCallback } from 'react';
import type { ScheduleResponse, SchedulerMode, SchedulerSettings } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseSchedulerResult {
  schedule: ScheduleResponse | null;
  settings: SchedulerSettings | null;
  mode: SchedulerMode;
  isLoading: boolean;
  error: Error | null;
  fetchSchedule: (agentId: string) => Promise<void>;
  updateMode: (mode: SchedulerMode) => Promise<void>;
  submitWorkload: (data: SubmitWorkloadData) => Promise<SubmitWorkloadResponse>;
  triggerEmergency: (agentId: string, reason: 'hurricane' | 'manual') => Promise<EmergencyResponse>;
}

interface SubmitWorkloadData {
  agent_id: string;
  type: 'BACKUP' | 'SYNC' | 'AI_TRAIN';
  size_gb: number;
  priority?: 'normal' | 'urgent';
}

interface SubmitWorkloadResponse {
  workload_id: string;
  scheduled_window: { start: string; end: string } | null;
  batch_queue_position: number | null;
  estimated_savings: string;
}

interface EmergencyResponse {
  job_id: string;
  status: string;
  eta_minutes: number;
}

export function useScheduler(): UseSchedulerResult {
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [settings, setSettings] = useState<SchedulerSettings | null>(null);
  const [mode, setMode] = useState<SchedulerMode>('balanced');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchSchedule = useCallback(async (agentId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/scheduler/schedule?agent_id=${agentId}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setSchedule(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateMode = useCallback(async (newMode: SchedulerMode) => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/scheduler/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: newMode }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setMode(data.mode);
      setSettings(data.effective_settings);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitWorkload = useCallback(async (data: SubmitWorkloadData): Promise<SubmitWorkloadResponse> => {
    const resp = await fetch(`${API_BASE}/api/v1/scheduler/workloads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }, []);

  const triggerEmergency = useCallback(async (agentId: string, reason: 'hurricane' | 'manual'): Promise<EmergencyResponse> => {
    const resp = await fetch(`${API_BASE}/api/v1/scheduler/emergency`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, reason }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }, []);

  return {
    schedule,
    settings,
    mode,
    isLoading,
    error,
    fetchSchedule,
    updateMode,
    submitWorkload,
    triggerEmergency,
  };
}
```

- [ ] **Step 3: Create useSchedulePolling hook**

Create `sunshift/dashboard/src/components/scheduler/hooks/useSchedulePolling.ts`:

```typescript
import { useEffect, useRef } from 'react';
import { useScheduler } from './useScheduler';

const POLL_INTERVAL_MS = 30000; // 30 seconds

export function useSchedulePolling(agentId: string, enabled: boolean = true) {
  const { schedule, fetchSchedule, isLoading, error } = useScheduler();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled || !agentId) return;

    // Initial fetch
    fetchSchedule(agentId);

    // Set up polling
    intervalRef.current = setInterval(() => {
      fetchSchedule(agentId);
    }, POLL_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [agentId, enabled, fetchSchedule]);

  return { schedule, isLoading, error };
}
```

- [ ] **Step 4: Create barrel export**

Create `sunshift/dashboard/src/components/scheduler/index.ts`:

```typescript
export * from './types';
export * from './hooks/useScheduler';
export * from './hooks/useSchedulePolling';
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/dashboard/src/components/scheduler/
git commit -m "feat(sp2): scheduler React hooks — useScheduler, useSchedulePolling, TypeScript types"
```

---

### Task 6: Dashboard Components — SchedulerCard

**Goal:** Create the main dashboard card showing scheduler status at a glance.

**Files:**
- Create: `sunshift/dashboard/src/components/scheduler/SchedulerCard.tsx`

**Steps:**

- [ ] **Step 1: Implement SchedulerCard**

Create `sunshift/dashboard/src/components/scheduler/SchedulerCard.tsx`:

```tsx
'use client';

import { useSchedulePolling } from './hooks/useSchedulePolling';
import type { SchedulerMode } from './types';

interface SchedulerCardProps {
  agentId: string;
  mode: SchedulerMode;
  onModeChange?: (mode: SchedulerMode) => void;
}

const modeColors: Record<SchedulerMode, string> = {
  conservative: 'text-yellow-500',
  balanced: 'text-green-500',
  aggressive: 'text-orange-500',
};

const modeLabels: Record<SchedulerMode, string> = {
  conservative: 'Conservative',
  balanced: 'Balanced',
  aggressive: 'Aggressive',
};

export function SchedulerCard({ agentId, mode, onModeChange }: SchedulerCardProps) {
  const { schedule, isLoading, error } = useSchedulePolling(agentId);

  if (isLoading && !schedule) {
    return (
      <div className="rounded-xl bg-zinc-900 border border-zinc-800 p-6 animate-pulse">
        <div className="h-6 bg-zinc-800 rounded w-1/3 mb-4" />
        <div className="h-20 bg-zinc-800 rounded mb-4" />
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-zinc-800 rounded" />
          <div className="h-16 bg-zinc-800 rounded" />
          <div className="h-16 bg-zinc-800 rounded" />
        </div>
      </div>
    );
  }

  const nextJob = schedule?.jobs.find(j => j.status === 'scheduled');
  const completedToday = schedule?.jobs.filter(j => j.status === 'completed').length ?? 0;
  const savedToday = 12; // TODO: Calculate from actual data

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  return (
    <div className="rounded-xl bg-zinc-900 border border-zinc-800 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wide">Scheduler Mode</p>
          <p className={`text-xl font-bold ${modeColors[mode]}`}>{modeLabels[mode]}</p>
        </div>
        <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">
          Active
        </span>
      </div>

      {/* Next Job */}
      <div className="rounded-lg bg-zinc-800/50 p-4 mb-4">
        <p className="text-xs text-zinc-500 mb-1">Next Scheduled Job</p>
        {nextJob ? (
          <>
            <p className="text-zinc-100">
              {formatTime(nextJob.window.start)} - {formatTime(nextJob.window.end)}
              <span className="text-zinc-500 ml-2">
                ({nextJob.workloads.length} workload{nextJob.workloads.length > 1 ? 's' : ''} batched)
              </span>
            </p>
            <p className="text-green-400 text-sm">Est. savings: $4.20</p>
          </>
        ) : (
          <p className="text-zinc-500">No jobs scheduled</p>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-blue-500/10 p-3 text-center">
          <p className="text-xl font-bold text-blue-400">{schedule?.batch_queue_status.count ?? 0}</p>
          <p className="text-xs text-zinc-500">In Queue</p>
        </div>
        <div className="rounded-lg bg-green-500/10 p-3 text-center">
          <p className="text-xl font-bold text-green-400">{completedToday}</p>
          <p className="text-xs text-zinc-500">Completed Today</p>
        </div>
        <div className="rounded-lg bg-purple-500/10 p-3 text-center">
          <p className="text-xl font-bold text-purple-400">${savedToday}</p>
          <p className="text-xs text-zinc-500">Saved Today</p>
        </div>
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-400">Error: {error.message}</p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Update barrel export**

Update `sunshift/dashboard/src/components/scheduler/index.ts`:

```typescript
export * from './types';
export * from './hooks/useScheduler';
export * from './hooks/useSchedulePolling';
export * from './SchedulerCard';
```

- [ ] **Step 3: Commit**

```bash
git add sunshift/dashboard/src/components/scheduler/
git commit -m "feat(sp2): SchedulerCard component — dashboard widget with stats"
```

---

### Task 7: Dashboard Components — ModeSelector

**Goal:** Create the preset mode selector with progressive disclosure.

**Files:**
- Create: `sunshift/dashboard/src/components/scheduler/ModeSelector.tsx`

**Steps:**

- [ ] **Step 1: Implement ModeSelector**

Create `sunshift/dashboard/src/components/scheduler/ModeSelector.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { CheckIcon } from '@heroicons/react/20/solid';
import type { SchedulerMode, SchedulerSettings } from './types';

interface ModeSelectorProps {
  currentMode: SchedulerMode;
  settings: SchedulerSettings | null;
  onModeChange: (mode: SchedulerMode) => void;
  isLoading?: boolean;
}

const modes: Array<{
  id: SchedulerMode;
  name: string;
  description: string;
}> = [
  {
    id: 'conservative',
    name: 'Conservative',
    description: 'Max safety, may miss some savings',
  },
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'Recommended for most users',
  },
  {
    id: 'aggressive',
    name: 'Aggressive',
    description: 'Max savings, longer wait times',
  },
];

export function ModeSelector({
  currentMode,
  settings,
  onModeChange,
  isLoading = false,
}: ModeSelectorProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="rounded-xl bg-zinc-900 border border-zinc-800 p-6">
      <h3 className="text-sm text-zinc-400 mb-4">Scheduler Mode</h3>

      <div className="space-y-2">
        {modes.map((mode) => {
          const isSelected = mode.id === currentMode;
          return (
            <button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              disabled={isLoading}
              className={`w-full p-4 rounded-lg text-left transition-all ${
                isSelected
                  ? 'bg-green-500/10 border-2 border-green-500'
                  : 'bg-zinc-800/50 border border-zinc-700 hover:border-zinc-600'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className={`font-medium ${isSelected ? 'text-green-400' : 'text-zinc-100'}`}>
                    {isSelected && <CheckIcon className="inline w-4 h-4 mr-1" />}
                    {mode.name}
                  </p>
                  <p className="text-sm text-zinc-500">{mode.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Advanced Settings Toggle */}
      <div className="mt-6 pt-4 border-t border-zinc-800">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-zinc-500 hover:text-zinc-400 transition-colors"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Settings
        </button>

        {showAdvanced && settings && (
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-zinc-500">Min Confidence</span>
              <span className="text-zinc-300">{(settings.min_confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Lookahead Horizon</span>
              <span className="text-zinc-300">{settings.lookahead_hours}h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Max Batch Wait</span>
              <span className="text-zinc-300">{settings.batch_wait_max_hours}h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Replan Frequency</span>
              <span className="text-zinc-300">{settings.replan_frequency_hours}h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Hurricane Trigger</span>
              <span className="text-zinc-300 capitalize">{settings.hurricane_trigger_level}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update barrel export**

Update `sunshift/dashboard/src/components/scheduler/index.ts`:

```typescript
export * from './types';
export * from './hooks/useScheduler';
export * from './hooks/useSchedulePolling';
export * from './SchedulerCard';
export * from './ModeSelector';
```

- [ ] **Step 3: Commit**

```bash
git add sunshift/dashboard/src/components/scheduler/
git commit -m "feat(sp2): ModeSelector component — preset modes with progressive disclosure"
```

---

### Task 8: Integration Tests + E2E Verification

**Goal:** Run full integration tests and verify end-to-end functionality.

**Files:**
- Modify: existing test files

**Acceptance Criteria:**
- [ ] All backend tests pass
- [ ] API endpoints respond correctly
- [ ] Dashboard components render without errors
- [ ] Coverage >80% for scheduler services

**Steps:**

- [ ] **Step 1: Run full backend test suite**

```bash
cd sunshift && uv run pytest tests/backend/ -v --cov=backend --cov-report=term-missing
```

Expected: All tests pass, coverage >80% for scheduler modules.

- [ ] **Step 2: Start backend and test API**

```bash
cd sunshift && docker compose up -d
sleep 5

# Test scheduler endpoints
curl -X POST http://localhost:8000/api/v1/scheduler/workloads \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"clinic-001","type":"BACKUP","size_gb":50}'

curl http://localhost:8000/api/v1/scheduler/schedule?agent_id=clinic-001

curl -X PUT http://localhost:8000/api/v1/scheduler/settings \
  -H "Content-Type: application/json" \
  -d '{"mode":"aggressive"}'

docker compose down
```

- [ ] **Step 3: Commit integration verification**

```bash
git add -A
git commit -m "test(sp2): integration tests passing, E2E verification complete"
```

---

## Verification — End-to-End Checklist

After all tasks complete:

1. `cd sunshift && uv run pytest tests/backend/ -v` → all tests pass
2. `docker compose up -d` → backend running
3. Submit workload: `curl -X POST localhost:8000/api/v1/scheduler/workloads -H 'Content-Type: application/json' -d '{"agent_id":"clinic-001","type":"BACKUP","size_gb":50}'`
4. Get schedule: `curl localhost:8000/api/v1/scheduler/schedule?agent_id=clinic-001`
5. Change mode: `curl -X PUT localhost:8000/api/v1/scheduler/settings -H 'Content-Type: application/json' -d '{"mode":"aggressive"}'`
6. Trigger emergency: `curl -X POST localhost:8000/api/v1/scheduler/emergency -H 'Content-Type: application/json' -d '{"agent_id":"clinic-001","reason":"hurricane"}'`
7. Dashboard renders SchedulerCard and ModeSelector without errors
