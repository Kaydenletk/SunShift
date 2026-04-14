"""Tests for Hurricane Shield API routes and prediction integration."""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.deps import get_shield_orchestrator


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    get_shield_orchestrator().deactivate_demo()  # cleanup


class TestHurricaneRoutes:
    async def test_get_status_returns_standby(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/hurricane/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "shield_mode" in data
        assert "active_threats" in data
        assert "max_threat_level" in data
        assert "storms" in data
        assert "last_check" in data

    async def test_demo_activate(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/hurricane/demo/activate")
        assert resp.status_code == 200
        assert resp.json()["shield_mode"] == "active"

    async def test_demo_deactivate(self, client: AsyncClient) -> None:
        await client.post("/api/v1/hurricane/demo/activate")
        resp = await client.post("/api/v1/hurricane/demo/deactivate")
        assert resp.status_code == 200
        assert resp.json()["shield_mode"] == "standby"

    async def test_demo_status_includes_storm(self, client: AsyncClient) -> None:
        await client.post("/api/v1/hurricane/demo/activate")
        resp = await client.get("/api/v1/hurricane/status")
        data = resp.json()
        assert data["shield_mode"] == "active"
        assert data["active_threats"] == 1
        assert data["max_threat_level"] == "critical"
        assert len(data["storms"]) == 1
        assert data["storms"][0]["name"] == "DEMO-STORM"

    async def test_prediction_includes_hurricane_status(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/predictions/energy")
        assert resp.status_code == 200
        data = resp.json()
        assert "hurricane_status" in data
        assert "active_threats" in data["hurricane_status"]
        assert "shield_mode" in data["hurricane_status"]
