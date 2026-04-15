"""Tests for scheduler API routes.

Tests all scheduler endpoints following TDD approach:
- POST /api/v1/scheduler/workloads - submit workload
- GET /api/v1/scheduler/schedule - get schedule for agent
- PUT /api/v1/scheduler/settings - update preset mode
- POST /api/v1/scheduler/emergency - trigger emergency
- DELETE /api/v1/scheduler/workloads/{id} - cancel workload
"""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture
async def client():
    """Create async test client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestSchedulerWorkloads:
    """Test workload submission endpoint."""

    async def test_submit_workload_returns_201(self, client):
        """POST /api/v1/scheduler/workloads should return 201 with workload_id."""
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
        """Urgent workloads should bypass batching and get scheduled_window."""
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "BACKUP",
            "size_gb": 60,
            "priority": "urgent",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scheduled_window"] is not None
        assert "start" in data["scheduled_window"]
        assert "end" in data["scheduled_window"]

    async def test_submit_small_workload_batches(self, client):
        """Small workloads should be added to batch queue."""
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "SYNC",
            "size_gb": 20,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["batch_queue_position"] is not None
        assert data["batch_queue_position"] > 0

    async def test_submit_large_workload_bypasses_batch(self, client):
        """Large workloads (≥50GB) should bypass batching."""
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "BACKUP",
            "size_gb": 75,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scheduled_window"] is not None

    async def test_submit_invalid_type_returns_422(self, client):
        """Invalid workload type should return 422 validation error."""
        resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "INVALID_TYPE",
            "size_gb": 50,
        })
        assert resp.status_code == 422


class TestSchedulerSchedule:
    """Test schedule retrieval endpoint."""

    async def test_get_schedule_returns_200(self, client):
        """GET /api/v1/scheduler/schedule should return schedule data."""
        resp = await client.get("/api/v1/scheduler/schedule", params={"agent_id": "clinic-001"})
        assert resp.status_code == 200
        data = resp.json()
        assert "jobs" in data
        assert "batch_queue_status" in data
        assert "cost_forecast" in data

    async def test_get_schedule_includes_batch_queue_status(self, client):
        """Schedule should include batch queue status."""
        resp = await client.get("/api/v1/scheduler/schedule", params={"agent_id": "clinic-001"})
        assert resp.status_code == 200
        data = resp.json()
        batch_status = data["batch_queue_status"]
        assert "count" in batch_status
        assert "total_size_gb" in batch_status

    async def test_get_schedule_includes_cost_forecast(self, client):
        """Schedule should include 48-hour cost forecast."""
        resp = await client.get("/api/v1/scheduler/schedule", params={"agent_id": "clinic-001"})
        assert resp.status_code == 200
        data = resp.json()
        forecast = data["cost_forecast"]
        assert len(forecast) <= 48
        if len(forecast) > 0:
            assert "hour" in forecast[0]
            assert "cost_cents_kwh" in forecast[0]
            assert "confidence" in forecast[0]


class TestSchedulerSettings:
    """Test settings update endpoint."""

    async def test_update_mode_to_aggressive(self, client):
        """PUT /api/v1/scheduler/settings should update mode."""
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "aggressive"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "aggressive"
        assert data["effective_settings"]["min_confidence"] == 0.60

    async def test_update_mode_to_conservative(self, client):
        """Conservative mode should have high confidence threshold."""
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "conservative"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "conservative"
        assert data["effective_settings"]["min_confidence"] == 0.90

    async def test_update_mode_to_balanced(self, client):
        """Balanced mode should use default settings."""
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "balanced"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "balanced"
        assert data["effective_settings"]["min_confidence"] == 0.75

    async def test_invalid_mode_returns_422(self, client):
        """Invalid mode should return 422 validation error."""
        resp = await client.put("/api/v1/scheduler/settings", json={"mode": "invalid"})
        assert resp.status_code == 422


class TestSchedulerEmergency:
    """Test emergency trigger endpoint."""

    async def test_trigger_emergency_hurricane(self, client):
        """POST /api/v1/scheduler/emergency should create emergency job."""
        resp = await client.post("/api/v1/scheduler/emergency", json={
            "agent_id": "clinic-001",
            "reason": "hurricane",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "executing"
        assert "job_id" in data
        assert "eta_minutes" in data

    async def test_trigger_emergency_manual(self, client):
        """Manual emergency trigger should work."""
        resp = await client.post("/api/v1/scheduler/emergency", json={
            "agent_id": "clinic-002",
            "reason": "manual",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "executing"
        assert "job_id" in data

    async def test_invalid_reason_returns_422(self, client):
        """Invalid emergency reason should return 422."""
        resp = await client.post("/api/v1/scheduler/emergency", json={
            "agent_id": "clinic-001",
            "reason": "invalid_reason",
        })
        assert resp.status_code == 422


class TestSchedulerCancellation:
    """Test workload cancellation endpoint."""

    async def test_cancel_nonexistent_workload_returns_404(self, client):
        """Cancelling nonexistent workload should return 404."""
        resp = await client.delete("/api/v1/scheduler/workloads/wl_nonexistent")
        assert resp.status_code == 404

    async def test_cancel_queued_workload_succeeds(self, client):
        """Cancelling queued workload should return success."""
        # First submit a small workload that will be queued
        submit_resp = await client.post("/api/v1/scheduler/workloads", json={
            "agent_id": "clinic-001",
            "type": "SYNC",
            "size_gb": 15,
        })
        workload_id = submit_resp.json()["workload_id"]

        # Then cancel it
        cancel_resp = await client.delete(f"/api/v1/scheduler/workloads/{workload_id}")
        assert cancel_resp.status_code == 200
        data = cancel_resp.json()
        assert data["cancelled"] is True
