import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.models.agent import AgentRegistration, AgentStatus
from backend.models.prediction import HourlyForecast, OptimalWindow, PredictionResponse
from backend.models.metrics import MetricsPayload
from backend.models.commands import AgentCommand, CommandResult


class TestAgentRegistration:
    def test_valid_registration(self):
        reg = AgentRegistration(agent_id="clinic-001", name="Dr. Nguyen Clinic")
        assert reg.agent_id == "clinic-001"
        assert reg.location == "tampa_fl"

    def test_invalid_agent_id_rejects_uppercase(self):
        with pytest.raises(ValidationError):
            AgentRegistration(agent_id="Clinic-001", name="Test")

    def test_invalid_agent_id_rejects_too_long(self):
        with pytest.raises(ValidationError):
            AgentRegistration(agent_id="a" * 65, name="Test")


class TestMetricsPayload:
    def test_valid_metrics(self):
        m = MetricsPayload(
            agent_id="clinic-001",
            timestamp=datetime.now(timezone.utc),
            cpu_percent=45.2,
            memory_percent=67.8,
            disk_percent=55.0,
            network_bytes_sent=1024,
            network_bytes_recv=2048,
        )
        assert m.cpu_percent == 45.2

    def test_rejects_negative_cpu(self):
        with pytest.raises(ValidationError):
            MetricsPayload(
                agent_id="x", timestamp=datetime.now(timezone.utc),
                cpu_percent=-1, memory_percent=0, disk_percent=0,
                network_bytes_sent=0, network_bytes_recv=0,
            )

    def test_rejects_cpu_over_100(self):
        with pytest.raises(ValidationError):
            MetricsPayload(
                agent_id="x", timestamp=datetime.now(timezone.utc),
                cpu_percent=101, memory_percent=0, disk_percent=0,
                network_bytes_sent=0, network_bytes_recv=0,
            )


class TestHourlyForecast:
    def test_valid_forecast(self):
        f = HourlyForecast(
            hour=datetime.now(timezone.utc),
            cost_cents_kwh=12.5,
            demand_mw=8000,
            confidence=0.91,
        )
        assert f.confidence == 0.91

    def test_rejects_confidence_over_1(self):
        with pytest.raises(ValidationError):
            HourlyForecast(
                hour=datetime.now(timezone.utc),
                cost_cents_kwh=12.5, demand_mw=8000, confidence=1.5,
            )


class TestAgentCommand:
    def test_valid_command(self):
        cmd = AgentCommand(
            command="START_SYNC",
            agent_id="clinic-001",
            issued_at=datetime.now(timezone.utc),
        )
        assert cmd.priority == "normal"

    def test_rejects_invalid_command(self):
        with pytest.raises(ValidationError):
            AgentCommand(
                command="DELETE_ALL",
                agent_id="clinic-001",
                issued_at=datetime.now(timezone.utc),
            )
