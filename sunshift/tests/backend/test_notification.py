"""Tests for the AlertGenerator notification service."""
import pytest

from backend.services.notification import AlertGenerator
from backend.services.hurricane_shield import StormInfo, ThreatLevel


class TestAlertGenerator:
    @pytest.fixture
    def generator(self) -> AlertGenerator:
        return AlertGenerator()  # no API key = template mode

    async def test_no_storms_returns_standby(self, generator: AlertGenerator) -> None:
        alert = await generator.generate_alert([], ThreatLevel.NONE)
        assert "standby" in alert.lower()

    async def test_critical_storm_mentions_backup(self, generator: AlertGenerator) -> None:
        storms = [StormInfo(name="MILTON", category=3, lat=26.0, lon=-83.0, wind_mph=120)]
        alert = await generator.generate_alert(storms, ThreatLevel.CRITICAL)
        assert "MILTON" in alert
        assert "backup" in alert.lower() or "backed up" in alert.lower()

    async def test_low_threat_mentions_standby(self, generator: AlertGenerator) -> None:
        storms = [StormInfo(name="WEAK", category=1, lat=20.0, lon=-60.0, wind_mph=75)]
        alert = await generator.generate_alert(storms, ThreatLevel.LOW)
        assert "standby" in alert.lower()

    async def test_medium_threat_mentions_monitoring(self, generator: AlertGenerator) -> None:
        storms = [StormInfo(name="WATCH", category=2, lat=25.0, lon=-80.0, wind_mph=100)]
        alert = await generator.generate_alert(storms, ThreatLevel.MEDIUM)
        assert "monitoring" in alert.lower()

    async def test_high_threat_mentions_backup(self, generator: AlertGenerator) -> None:
        storms = [StormInfo(name="DANGER", category=4, lat=27.0, lon=-83.0, wind_mph=150)]
        alert = await generator.generate_alert(storms, ThreatLevel.HIGH)
        assert "backed up" in alert.lower() or "backup" in alert.lower()
