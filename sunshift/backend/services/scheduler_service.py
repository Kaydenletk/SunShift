"""Scheduler Service — Hybrid algorithm (Greedy + Lookahead + Batching).

This is the core AI Scheduler that decides WHEN to migrate workloads based on:
- TOU pricing forecasts from ML Engine
- Hurricane alerts from Hurricane Shield
- Workload urgency and deadlines
- Batch queue status

Decision Flow:
1. Hurricane active? → GREEDY (execute NOW)
2. Urgent/deadline? → GREEDY (best in 6h)
3. Flexible? → LOOKAHEAD (best in 48h)
4. Batchable (<50GB)? → Add to batch queue
5. Large (≥50GB)? → Schedule solo

The scheduler uses probabilistic window scoring (savings × confidence²) to
handle forecast uncertainty intelligently.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.models.scheduler import (
    CostWindow,
    JobStatus,
    Priority,
    RiskLevel,
    ScheduledJob,
    SchedulerSettings,
    TimeWindow,
    Workload,
    WorkloadType,
)
from backend.services.batching_service import BatchingService
from backend.services.window_scoring import WindowScorer
from backend.services.hurricane_shield import ShieldOrchestrator


class ScheduleMode(str, enum.Enum):
    """Scheduling mode determines time horizon and urgency.

    GREEDY: Next available window, used for urgent/hurricane scenarios.
    LOOKAHEAD: Best window in 48h horizon, used for flexible workloads.
    """

    GREEDY = "greedy"
    LOOKAHEAD = "lookahead"


class SchedulerService:
    """Hybrid scheduler implementing the decision flow from spec.

    The scheduler coordinates three subsystems:
    1. WindowScorer: Scores windows using probabilistic formula
    2. BatchingService: Manages workload batching for efficiency
    3. ShieldOrchestrator: Monitors hurricane alerts

    Attributes:
        settings: Scheduler configuration (min confidence, horizons, etc).
        batching: Batching service for aggregating small workloads.
        scorer: Window scorer using probabilistic formula.
        shield: Hurricane shield orchestrator.
        _scheduled_jobs: In-memory cache of scheduled jobs.
    """

    GREEDY_HORIZON_HOURS = 6
    LOOKAHEAD_HORIZON_HOURS = 48

    def __init__(self, settings: SchedulerSettings) -> None:
        """Initialize the scheduler with given settings.

        Args:
            settings: Scheduler configuration.
        """
        self.settings = settings
        self.batching = BatchingService(settings)
        self.scorer = WindowScorer()
        self.shield = ShieldOrchestrator()
        self._scheduled_jobs: dict[str, ScheduledJob] = {}

    def _determine_mode(
        self, workload: Workload, hurricane_active: bool
    ) -> ScheduleMode:
        """Determine scheduling mode based on workload and conditions.

        Decision logic:
        1. Hurricane active → GREEDY (override everything)
        2. Urgent priority → GREEDY
        3. Has deadline → GREEDY
        4. Otherwise → LOOKAHEAD

        Args:
            workload: The workload to schedule.
            hurricane_active: Whether hurricane shield is active.

        Returns:
            ScheduleMode (GREEDY or LOOKAHEAD).
        """
        if hurricane_active:
            return ScheduleMode.GREEDY

        if workload.priority == Priority.URGENT:
            return ScheduleMode.GREEDY

        if workload.deadline is not None:
            return ScheduleMode.GREEDY

        return ScheduleMode.LOOKAHEAD

    def _score_window(self, window: CostWindow) -> float:
        """Score a window using probabilistic formula.

        Args:
            window: The cost window to score.

        Returns:
            Score (higher is better).
        """
        return self.scorer.score_window(window).score

    def _find_best_window_greedy(self, windows: list[CostWindow]) -> CostWindow:
        """Find best window within greedy horizon (6h).

        Args:
            windows: List of cost windows to search.

        Returns:
            Best window within GREEDY_HORIZON_HOURS.
        """
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=self.GREEDY_HORIZON_HOURS)

        # Filter to greedy horizon
        candidates = [w for w in windows if w.start <= cutoff]
        if not candidates:
            # Fall back to first N windows if filtering removed all
            candidates = windows[: self.GREEDY_HORIZON_HOURS]

        # Return highest scoring window
        return max(candidates, key=self._score_window)

    def _find_best_window_lookahead(self, windows: list[CostWindow]) -> CostWindow:
        """Find best window within lookahead horizon (48h).

        Applies minimum confidence filter from settings.

        Args:
            windows: List of cost windows to search.

        Returns:
            Best window within lookahead horizon that meets min confidence.
        """
        horizon = self.settings.lookahead_hours
        candidates = windows[:horizon]

        # Filter by minimum confidence
        filtered = [
            w for w in candidates if w.confidence >= self.settings.min_confidence
        ]

        if not filtered:
            # Fall back to all candidates if none meet confidence threshold
            filtered = candidates

        # Return highest scoring window
        return max(filtered, key=self._score_window)

    def _get_cost_windows(self) -> list[CostWindow]:
        """Get cost forecast from ML Engine.

        TODO: Replace with real ML Engine integration from SP1.

        Returns:
            List of 48 hourly cost windows.
        """
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        windows = []

        for i in range(48):
            hour = (now.hour + i) % 24

            # Simulate FPL TOU pattern
            if 12 <= hour < 21:
                cost = 23.0
                conf = 0.75
            elif 6 <= hour < 12:
                cost = 12.0
                conf = 0.85
            else:
                cost = 6.0
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

    def _is_hurricane_active(self) -> bool:
        """Check if hurricane shield is active.

        Returns:
            True if shield is in active mode.
        """
        return self.shield.status.shield_mode == "active"

    async def schedule_workload(self, workload: Workload) -> ScheduledJob | None:
        """Main scheduling entry point.

        Decision flow:
        1. Determine mode (Greedy vs Lookahead) based on urgency/hurricane
        2. Check if workload should bypass batching (large or urgent)
        3. If batchable: add to queue, flush if conditions met
        4. If bypass: schedule immediately in best window

        Args:
            workload: The workload to schedule.

        Returns:
            ScheduledJob if scheduled immediately, None if batched.
        """
        hurricane_active = self._is_hurricane_active()
        mode = self._determine_mode(workload, hurricane_active)
        windows = self._get_cost_windows()

        # Check if workload should bypass batching
        result = self.batching.add_to_queue(workload)

        if result.queued:
            # Workload was added to batch queue
            # Check if we should flush
            should_flush = self.batching.should_flush()

            if should_flush:
                # Flush the batch queue
                target = self._find_best_window_lookahead(windows)
                job = self.batching.create_batch_job(target)

                if job:
                    self._scheduled_jobs[job.id] = job
                    return job

            # Still batching, not ready to flush
            return None

        # Workload bypassed batching (large or urgent)
        # Schedule immediately
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
        """Find optimal windows in the given horizon.

        Args:
            horizon_hours: Number of hours to look ahead.

        Returns:
            Top 5 ranked windows.
        """
        windows = self._get_cost_windows()[:horizon_hours]
        ranked = self.scorer.rank_windows(windows, top_n=5)
        return [sw.window for sw in ranked]

    def get_scheduled_jobs(self, agent_id: str | None = None) -> list[ScheduledJob]:
        """Get all scheduled jobs, optionally filtered by agent.

        Args:
            agent_id: Optional agent ID to filter by.

        Returns:
            List of scheduled jobs.
        """
        jobs = list(self._scheduled_jobs.values())

        if agent_id:
            jobs = [
                j for j in jobs if any(w.agent_id == agent_id for w in j.workloads)
            ]

        return jobs

    async def trigger_emergency(self, agent_id: str, reason: str) -> ScheduledJob:
        """Trigger emergency backup for hurricane or manual override.

        Creates an immediate job that starts NOW.

        Args:
            agent_id: ID of the agent requesting emergency backup.
            reason: Reason for emergency (hurricane or manual).

        Returns:
            ScheduledJob with status RUNNING.
        """
        # Create immediate job starting now
        now = datetime.now(timezone.utc)

        # Try to get pending workloads from batch queue for this agent
        pending_workloads = []
        for wl in self.batching._workloads:
            if wl.agent_id == agent_id:
                pending_workloads.append(wl)

        # If no pending workloads, create a placeholder emergency workload
        if not pending_workloads:
            pending_workloads = [
                Workload(
                    id=f"wl_emergency_{uuid.uuid4().hex[:8]}",
                    agent_id=agent_id,
                    type=WorkloadType.BACKUP,
                    size_gb=0,
                    priority=Priority.URGENT,
                    created_at=now,
                )
            ]

        job = ScheduledJob(
            id=f"job_emergency_{uuid.uuid4().hex[:8]}",
            workloads=pending_workloads,
            window=TimeWindow(start=now, end=now + timedelta(hours=4)),
            estimated_cost=Decimal("0"),
            confidence=1.0,
            status=JobStatus.RUNNING,
        )

        self._scheduled_jobs[job.id] = job
        return job

    async def replan_on_forecast_update(self) -> list[ScheduledJob]:
        """Replan scheduled jobs when forecast updates.

        Only reschedules if new window is significantly better (>10% improvement).

        Returns:
            List of jobs that were rescheduled.
        """
        windows = self._get_cost_windows()
        updated = []

        for job_id, job in self._scheduled_jobs.items():
            if job.status != JobStatus.SCHEDULED:
                continue

            # Find new best window
            best = self._find_best_window_lookahead(windows)

            # Estimate current window score
            current_score = self._score_window(
                CostWindow(
                    start=job.window.start,
                    end=job.window.end,
                    avg_cost_cents_kwh=15.0,  # Estimated average
                    confidence=job.confidence,
                    weather_risk=RiskLevel.LOW,
                )
            )
            new_score = self._score_window(best)

            # Only reschedule if significantly better (>10% improvement)
            if new_score > current_score * 1.1:
                job.window = TimeWindow(start=best.start, end=best.end)
                job.confidence = best.confidence
                updated.append(job)

        return updated
