# AI Scheduler Design Specification

> **Status:** Approved
> **Date:** 2026-04-15
> **Sub-project:** SP2 — AI Scheduler
> **Parent:** [SunShift MVP Design](./2026-04-13-sunshift-mvp-design.md)

## Overview

The AI Scheduler is SunShift's core intelligence layer that decides **when** to migrate workloads between on-premise and AWS based on electricity TOU pricing forecasts and hurricane alerts. It implements a **Hybrid algorithm** combining Greedy (for urgency), Lookahead (for optimization), and Batching (for efficiency).

### Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority Order | Safety First | Hurricane > Cost Savings > User Preferences > Workload Constraints |
| Algorithm | Hybrid (Greedy + Lookahead + Batching) | Best of all approaches |
| Lookahead Horizon | 48h | Matches ML model accuracy |
| Uncertainty Handling | Probabilistic (confidence²) | Weights uncertainty appropriately |
| Batching Strategy | Balanced (2 jobs, 2h wait, 4h window) | Good efficiency without long waits |
| Hurricane Trigger | Balanced (Warning OR <200mi) | Reasonable safety margin |
| User Control | Moderate (preset modes + progressive disclosure) | Simple defaults, power available |
| Implementation | Full (2-3 weeks) | Complete feature set for portfolio |

---

## Section 1: Algorithm Core

### Decision Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        WORKLOAD ARRIVES                          │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Hurricane Alert?  │
                    │   (Warning/200mi)  │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │ YES                           │ NO
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │  GREEDY MODE    │             │  Check Urgency  │
    │  Next available │             │  (deadline set?)│
    │  window, NOW    │             └────────┬────────┘
    └─────────────────┘                      │
                                  ┌──────────┴──────────┐
                                  │ URGENT              │ FLEXIBLE
                                  ▼                     ▼
                        ┌─────────────────┐   ┌─────────────────┐
                        │  GREEDY MODE    │   │  LOOKAHEAD MODE │
                        │  Best slot in   │   │  Best slot in   │
                        │  next 6 hours   │   │  next 48 hours  │
                        └─────────────────┘   └────────┬────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │  Batchable?     │
                                              │  (size < 50GB)  │
                                              └────────┬────────┘
                                                       │
                                            ┌──────────┴──────────┐
                                            │ YES                 │ NO
                                            ▼                     ▼
                                  ┌─────────────────┐   ┌─────────────────┐
                                  │  BATCH QUEUE    │   │  Schedule solo  │
                                  │  Wait up to 2h  │   │  in best window │
                                  │  for more jobs  │   └─────────────────┘
                                  └─────────────────┘
```

### Core Data Structures

#### Workload
```python
@dataclass
class Workload:
    id: str                          # "wl_abc123"
    agent_id: str                    # "clinic-001"
    type: WorkloadType               # BACKUP | SYNC | AI_TRAIN
    size_gb: int                     # 50
    priority: Priority               # normal | urgent
    deadline: datetime | None        # Optional hard deadline
    created_at: datetime
```

#### ScheduledJob
```python
@dataclass
class ScheduledJob:
    id: str                          # "job_xyz789"
    workloads: list[Workload]        # Can contain multiple batched workloads
    window: TimeWindow               # start, end
    estimated_cost: Decimal          # $12.50
    confidence: float                # 0.85
    status: JobStatus                # scheduled | running | completed | failed
```

#### CostWindow
```python
@dataclass
class CostWindow:
    start: datetime
    end: datetime
    avg_cost_cents_kwh: float        # 8.5
    confidence: float                # 0.92
    score: float                     # Calculated: savings × confidence²
    weather_risk: RiskLevel          # low | medium | high
```

#### BatchQueue
```python
@dataclass
class BatchQueue:
    workloads: list[Workload]
    total_size_gb: int               # 80
    oldest_arrival: datetime
    target_window: CostWindow
    flush_at: datetime               # Max 2h from oldest_arrival
```

### Scoring Formula

```
window_score = (peak_cost - window_cost) × confidence² × duration_hours
```

**Example:**
- Peak cost: 25¢/kWh
- Window cost: 8¢/kWh
- Confidence: 0.85
- Duration: 4 hours

```
Score = (25 - 8) × 0.85² × 4 = 17 × 0.7225 × 4 = $49.13 savings score
```

The confidence² term ensures that uncertain forecasts are penalized quadratically, preferring reliable windows over potentially better but uncertain ones.

### Batching Rules

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Min jobs to flush | 2 | Efficiency threshold |
| Max wait time | 2 hours | User experience |
| Max batch window | 4 hours | Operational bound |
| Max batch size | 200 GB | Network/storage limit |
| Bypass threshold | 50 GB | Large jobs run solo |

### Hurricane Override Logic

```python
def should_trigger_emergency(alert: NOAAAlert, location: Coordinates) -> bool:
    """
    Trigger emergency mode if:
    1. Alert level is WARNING or higher, OR
    2. Storm distance is under 200 miles from Tampa
    """
    if alert.level in [AlertLevel.WARNING, AlertLevel.EMERGENCY]:
        return True

    distance = calculate_distance(alert.storm_center, TAMPA_COORDINATES)
    return distance < 200  # miles
```

---

## Section 2: API Endpoints

### New REST Endpoints

#### POST /api/v1/scheduler/workloads
Submit a new workload for scheduling.

```python
# Request
class WorkloadSubmitRequest(BaseModel):
    agent_id: str
    type: Literal["BACKUP", "SYNC", "AI_TRAIN"]
    size_gb: int
    priority: Literal["normal", "urgent"] = "normal"
    deadline: datetime | None = None

# Response
class WorkloadSubmitResponse(BaseModel):
    workload_id: str
    scheduled_window: TimeWindow | None  # None if batched
    batch_queue_position: int | None     # Position if batched
    estimated_savings: Decimal
```

#### GET /api/v1/scheduler/schedule
Get current schedule for next 48 hours.

```python
# Query: ?agent_id=clinic-001

# Response
class ScheduleResponse(BaseModel):
    jobs: list[ScheduledJob]
    next_window: CostWindow
    batch_queue_status: BatchQueueStatus
    cost_forecast: list[HourlyCost]  # 48h forecast
```

#### PUT /api/v1/scheduler/settings
Update scheduler preset mode.

```python
# Request
class SettingsUpdateRequest(BaseModel):
    mode: Literal["conservative", "balanced", "aggressive"]

# Response
class SettingsUpdateResponse(BaseModel):
    mode: str
    effective_settings: SchedulerSettings
```

#### POST /api/v1/scheduler/emergency
Trigger emergency backup (hurricane override).

```python
# Request
class EmergencyRequest(BaseModel):
    agent_id: str
    reason: Literal["hurricane", "manual"]

# Response
class EmergencyResponse(BaseModel):
    job_id: str
    status: Literal["executing"]
    eta_minutes: int
```

#### DELETE /api/v1/scheduler/workloads/{id}
Cancel a scheduled workload.

```python
# Response
class CancelResponse(BaseModel):
    cancelled: bool
    refunded_to_queue: bool
```

### Internal Services

#### SchedulerService
Core scheduling logic.

```python
class SchedulerService:
    def schedule_workload(self, workload: Workload) -> ScheduledJob
    def find_optimal_windows(self, horizon_hours: int = 48) -> list[CostWindow]
    def score_windows(self, windows: list[CostWindow]) -> list[ScoredWindow]
    def replan_on_forecast_update(self) -> list[ScheduledJob]
```

#### BatchingService
Manages the batch queue.

```python
class BatchingService:
    def add_to_queue(self, workload: Workload) -> BatchQueueStatus
    def should_flush(self) -> tuple[bool, str]  # (should_flush, reason)
    def create_batch_job(self) -> ScheduledJob
    def cleanup_stale_batches(self) -> int  # Returns count cleaned
```

#### HurricaneMonitor
Monitors NOAA alerts and triggers emergency mode.

```python
class HurricaneMonitor:
    def check_noaa_alerts(self) -> list[NOAAAlert]
    def evaluate_threat_level(self, alert: NOAAAlert) -> ThreatLevel
    def trigger_emergency_mode(self, agent_ids: list[str]) -> list[str]  # Returns triggered job IDs
```

#### JobExecutor
Executes scheduled jobs.

```python
class JobExecutor:
    async def execute_at_window(self, job: ScheduledJob) -> JobResult
    async def notify_agent_websocket(self, agent_id: str, event: JobEvent)
    def track_progress(self, job_id: str) -> JobProgress
    async def handle_failure(self, job: ScheduledJob, error: Exception) -> RetryDecision
```

---

## Section 3: Dashboard Integration

### New Components

#### SchedulerCard (Main Dashboard)
Primary widget showing scheduler status at a glance.

```
┌─────────────────────────────────────────┐
│ SCHEDULER MODE          ┌──────────┐   │
│ Balanced               │  Active   │   │
│                        └──────────┘   │
│ ┌─────────────────────────────────┐   │
│ │ Next Scheduled Job              │   │
│ │ 2:00 AM - 4:00 AM (3 batched)   │   │
│ │ Est. savings: $4.20             │   │
│ └─────────────────────────────────┘   │
│                                        │
│  ┌────────┐ ┌────────┐ ┌────────┐     │
│  │   2    │ │   5    │ │  $12   │     │
│  │In Queue│ │Complete│ │ Saved  │     │
│  └────────┘ └────────┘ └────────┘     │
└─────────────────────────────────────────┘
```

#### ScheduleTimeline (48h View)
Visual timeline showing cost windows and scheduled jobs.

```
Cost Level:  ████ Low  ████ Medium  ████ Peak

     12AM   6AM   12PM   6PM   12AM
       │     │      │     │      │
       ▓▓▓▓▓▓░░░░░░████████░░░░▓▓▓▓
       │                         │
       └── Scheduled: 2-4 AM ────┘
           85% confidence
```

#### ModeSelector (Settings)
Preset mode picker with progressive disclosure.

```
┌─────────────────────────────────────┐
│ Scheduler Mode                      │
│                                     │
│ ○ Conservative                      │
│   Max safety, may miss some savings │
│                                     │
│ ● Balanced ✓                        │
│   Recommended for most users        │
│                                     │
│ ○ Aggressive                        │
│   Max savings, longer wait times    │
│                                     │
│ ─────────────────────────────────── │
│ ▶ Advanced Settings                 │
└─────────────────────────────────────┘
```

#### BatchQueueStatus
Shows workloads waiting to be batched.

```
┌─────────────────────────────────────┐
│ Batch Queue                         │
│                                     │
│ patient-records/    25 GB  Waiting  │
│ Arrived 10:30 AM                    │
│                                     │
│ case-files/         15 GB  Waiting  │
│ Arrived 11:15 AM                    │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Batch executes at 2:00 AM      │ │
│ │ 40 GB total                    │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Component File Structure

```
dashboard/src/components/scheduler/
├── SchedulerCard.tsx        # Main dashboard card
├── ScheduleTimeline.tsx     # 48h timeline visualization
├── ModeSelector.tsx         # Preset mode picker
├── BatchQueueStatus.tsx     # Queue display
├── AdvancedSettings.tsx     # Progressive disclosure panel
├── EmergencyButton.tsx      # Manual hurricane trigger
└── hooks/
    ├── useScheduler.ts      # API calls + state
    └── useSchedulePolling.ts # Real-time updates
```

### Preset Mode Settings

| Setting | Conservative | Balanced | Aggressive |
|---------|-------------|----------|------------|
| Min confidence | 90% | 75% | 60% |
| Lookahead horizon | 24h | 48h | 48h |
| Batch wait max | 1h | 2h | 4h |
| Replan frequency | 2h | 6h | 12h |
| Hurricane trigger | Watch level | Warning level | Warning level |

---

## Section 4: Testing Strategy

### Test Pyramid

```
          ┌─────────────┐
          │    E2E      │  5 scenarios
          │  (Slowest)  │
          ├─────────────┤
          │ Integration │  15 tests
          │             │
          ├─────────────┤
          │    Unit     │  50+ tests
          │  (Fastest)  │  Target: 80% coverage
          └─────────────┘
```

### Unit Tests (Backend)

#### test_scheduler_service.py
```python
def test_greedy_selects_next_cheap_slot()
def test_lookahead_finds_optimal_48h_window()
def test_hurricane_triggers_greedy_override()
def test_confidence_scoring_weights_correctly()
def test_replan_updates_scheduled_jobs()
```

#### test_batching_service.py
```python
def test_adds_small_workload_to_queue()
def test_flushes_after_2h_wait()
def test_flushes_when_min_jobs_reached()
def test_large_workload_bypasses_queue()
def test_urgent_workload_bypasses_queue()
```

#### test_hurricane_monitor.py
```python
def test_warning_level_triggers_emergency()
def test_distance_under_200mi_triggers()
def test_advisory_does_not_trigger()
def test_threat_level_calculation()
```

#### test_window_scoring.py
```python
def test_score_formula_correct()
def test_low_confidence_reduces_score()
def test_longer_window_higher_score()
def test_ranks_windows_correctly()
```

### Integration Tests

```python
# test_scheduler_api.py — FastAPI TestClient

async def test_submit_workload_returns_scheduled_window():
    response = await client.post("/api/v1/scheduler/workloads", json={
        "agent_id": "clinic-001", "type": "BACKUP", "size_gb": 50
    })
    assert response.status_code == 201
    assert "scheduled_window" in response.json()
    assert response.json()["estimated_savings"] > 0

async def test_emergency_override_ignores_schedule():
    # Schedule a job for 2 AM
    await client.post("/api/v1/scheduler/workloads", json={...})

    # Trigger emergency
    response = await client.post("/api/v1/scheduler/emergency", json={
        "agent_id": "clinic-001", "reason": "hurricane"
    })
    assert response.json()["status"] == "executing"  # Immediate, not scheduled

async def test_batch_queue_accumulates_workloads():
    await client.post("/api/v1/scheduler/workloads", json={"size_gb": 20, ...})
    await client.post("/api/v1/scheduler/workloads", json={"size_gb": 25, ...})

    schedule = await client.get("/api/v1/scheduler/schedule?agent_id=clinic-001")
    assert schedule.json()["batch_queue_status"]["count"] == 2
```

### E2E Simulation Scenarios

| ID | Scenario | Steps | Verification |
|----|----------|-------|--------------|
| E2E-1 | Normal Day Scheduling | Submit 5 workloads across day | All scheduled in off-peak windows, savings calculated correctly |
| E2E-2 | Hurricane Override | Mock NOAA Warning | All scheduled jobs immediately execute, notification sent |
| E2E-3 | Batch Flush | Submit 3 small workloads within 1h | Batched into single job, execute together |
| E2E-4 | Forecast Update Replan | Schedule job for 2 AM, mock better 4 AM window | Job rescheduled to 4 AM |
| E2E-5 | Mode Switch | Switch Balanced → Aggressive | Longer wait times observed, higher savings |

### Coverage Requirements

| Component | Target | Rationale |
|-----------|--------|-----------|
| SchedulerService | 90% | Core business logic |
| BatchingService | 85% | Critical for efficiency |
| HurricaneMonitor | 95% | Safety-critical |
| API Endpoints | 80% | Standard coverage |
| Dashboard Components | 70% | UI testing via E2E |

---

## Implementation Notes

### Dependencies on Other Sub-projects

- **SP1 (Core Pipeline + ML Engine)**: Scheduler depends on cost forecasts from ML Engine
- **SP3 (Hurricane Shield)**: Scheduler integrates with NOAA alert monitoring

### Rollout Strategy

1. **Phase 1**: Backend services + API endpoints
2. **Phase 2**: Dashboard components + integration
3. **Phase 3**: E2E testing + polish

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ML forecast inaccuracy | Probabilistic scoring penalizes uncertainty |
| Hurricane false positives | Balanced trigger threshold avoids over-reaction |
| Batch delays frustrate users | 2h max wait, progress visibility in UI |
| Complex settings confuse users | Preset modes hide complexity |

---

## Appendix: FPL TOU Reference

| Period | Hours | Rate | Multiplier |
|--------|-------|------|------------|
| Off-Peak | 9 PM - 6 AM | ~5¢/kWh | 1.0x |
| Shoulder | 6 AM - 12 PM | ~12¢/kWh | 2.4x |
| Peak | 12 PM - 9 PM | ~23¢/kWh | 4.6x |

*Rates are approximate and vary seasonally. The ML Engine provides precise forecasts.*
