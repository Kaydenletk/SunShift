"""API route tests for SunShift SP1 backend."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
import backend.core.deps as deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transport() -> ASGITransport:
    return ASGITransport(app=app)


def _clear_stores() -> None:
    """Reset in-memory stores between tests."""
    deps._agent_store.clear()
    deps._metrics_store.clear()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_stores():
    """Clear in-memory stores before every test."""
    _clear_stores()
    yield
    _clear_stores()


# ---------------------------------------------------------------------------
# Agent registration tests
# ---------------------------------------------------------------------------


class TestAgentRegistration:
    async def test_register_agent_returns_201(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/api/v1/agents/register",
                json={
                    "agent_id": "agent-alpha",
                    "name": "Alpha Node",
                    "location": "tampa_fl",
                    "watch_paths": ["/data"],
                },
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["agent_id"] == "agent-alpha"
        assert body["status"] == "online"

    async def test_register_duplicate_returns_409(self):
        transport = _make_transport()
        payload = {
            "agent_id": "agent-beta",
            "name": "Beta Node",
            "location": "tampa_fl",
            "watch_paths": [],
        }
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            await c.post("/api/v1/agents/register", json=payload)
            resp = await c.post("/api/v1/agents/register", json=payload)
        assert resp.status_code == 409

    async def test_register_invalid_agent_id_returns_422(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/api/v1/agents/register",
                json={
                    "agent_id": "INVALID AGENT ID!",
                    "name": "Bad",
                    "location": "tampa_fl",
                    "watch_paths": [],
                },
            )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Agent status tests
# ---------------------------------------------------------------------------


class TestAgentStatus:
    async def test_get_status_returns_200(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            await c.post(
                "/api/v1/agents/register",
                json={
                    "agent_id": "agent-gamma",
                    "name": "Gamma",
                    "location": "tampa_fl",
                    "watch_paths": [],
                },
            )
            resp = await c.get("/api/v1/agents/status/agent-gamma")
        assert resp.status_code == 200
        assert resp.json()["agent_id"] == "agent-gamma"

    async def test_get_status_unknown_returns_404(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.get("/api/v1/agents/status/does-not-exist")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Metrics ingestion tests
# ---------------------------------------------------------------------------


class TestMetricsIngestion:
    async def test_ingest_metrics_returns_202(self):
        transport = _make_transport()
        payload = {
            "agent_id": "agent-delta",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 42.5,
            "memory_percent": 60.0,
            "disk_percent": 30.0,
            "network_bytes_sent": 1024,
            "network_bytes_recv": 2048,
            "estimated_power_watts": 150.0,
        }
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post("/api/v1/metrics/ingest", json=payload)
        assert resp.status_code == 202
        body = resp.json()
        assert body["accepted"] is True
        assert body["agent_id"] == "agent-delta"

    async def test_ingest_invalid_metrics_returns_422(self):
        transport = _make_transport()
        payload = {
            "agent_id": "agent-epsilon",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 999,  # > 100, invalid
            "memory_percent": 60.0,
            "disk_percent": 30.0,
            "network_bytes_sent": 1024,
            "network_bytes_recv": 2048,
        }
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post("/api/v1/metrics/ingest", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Prediction tests
# ---------------------------------------------------------------------------


class TestPredictions:
    async def test_get_energy_prediction_returns_200(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.get("/api/v1/predictions/energy")
        assert resp.status_code == 200
        body = resp.json()
        assert body["location"] == "tampa_fl"
        assert len(body["hourly_forecast"]) == 48
        assert "optimal_windows" in body
        assert "prediction_id" in body
        assert "explanation" in body

    async def test_get_energy_prediction_custom_location(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.get("/api/v1/predictions/energy?location=miami_fl")
        assert resp.status_code == 200
        assert resp.json()["location"] == "miami_fl"


# ---------------------------------------------------------------------------
# Command dispatch tests
# ---------------------------------------------------------------------------


class TestCommandDispatch:
    async def test_dispatch_command_to_known_agent(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            # Register first
            await c.post(
                "/api/v1/agents/register",
                json={
                    "agent_id": "agent-zeta",
                    "name": "Zeta",
                    "location": "tampa_fl",
                    "watch_paths": [],
                },
            )
            resp = await c.post(
                "/api/v1/commands/dispatch",
                json={
                    "command": "START_SYNC",
                    "agent_id": "agent-zeta",
                    "issued_at": datetime.now(timezone.utc).isoformat(),
                    "paths": ["/data"],
                    "priority": "normal",
                },
            )
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "queued"
        assert body["agent_id"] == "agent-zeta"

    async def test_dispatch_command_unknown_agent_returns_404(self):
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/api/v1/commands/dispatch",
                json={
                    "command": "STOP",
                    "agent_id": "ghost-agent",
                    "issued_at": datetime.now(timezone.utc).isoformat(),
                    "paths": [],
                    "priority": "normal",
                },
            )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# WebSocket tests
# ---------------------------------------------------------------------------


class TestWebSocket:
    async def test_websocket_connect_and_heartbeat(self):
        """WebSocket accepts connection and acknowledges heartbeats."""
        transport = _make_transport()
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            # Register agent first so status updates work
            await c.post(
                "/api/v1/agents/register",
                json={
                    "agent_id": "agent-ws-01",
                    "name": "WS Test Node",
                    "location": "tampa_fl",
                    "watch_paths": [],
                },
            )

        from starlette.testclient import TestClient

        client = TestClient(app)
        with client.websocket_connect("/ws/agent/agent-ws-01") as ws:
            # Should receive a "connected" acknowledgement
            data = ws.receive_json()
            assert data["type"] == "connected"
            assert data["agent_id"] == "agent-ws-01"

            # Send a heartbeat
            ws.send_json({"type": "heartbeat"})
            ack = ws.receive_json()
            assert ack["type"] == "heartbeat_ack"
            assert ack["agent_id"] == "agent-ws-01"

    async def test_websocket_unknown_message_type(self):
        """WebSocket returns error for unknown message types."""
        from starlette.testclient import TestClient

        # Register the agent
        deps._agent_store["agent-ws-02"] = deps.AgentStatus(
            agent_id="agent-ws-02",
            status="online",
            last_seen=datetime.now(timezone.utc),
        )

        client = TestClient(app)
        with client.websocket_connect("/ws/agent/agent-ws-02") as ws:
            ws.receive_json()  # consume "connected"
            ws.send_json({"type": "unknown_msg"})
            resp = ws.receive_json()
            assert resp["type"] == "error"
