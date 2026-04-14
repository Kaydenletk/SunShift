# tests/backend/test_hurricane_shield.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.services.hurricane_shield import (
    NOAAClient, ThreatEvaluator, ThreatLevel, StormInfo,
    haversine_km,
)

class TestHaversine:
    def test_tampa_to_miami(self):
        # Tampa (27.95, -82.46) to Miami (25.76, -80.19) ~= 332km
        dist = haversine_km(27.95, -82.46, 25.76, -80.19)
        assert 320 < dist < 345

    def test_same_point_is_zero(self):
        assert haversine_km(27.95, -82.46, 27.95, -82.46) == 0

class TestThreatEvaluator:
    def test_distant_storm_is_none(self):
        evaluator = ThreatEvaluator(target_lat=27.95, target_lon=-82.46)
        storm = StormInfo(name="Test", category=1, lat=15.0, lon=-50.0, wind_mph=80)
        assert evaluator.evaluate(storm) == ThreatLevel.NONE

    def test_close_cat3_is_critical(self):
        evaluator = ThreatEvaluator(target_lat=27.95, target_lon=-82.46)
        storm = StormInfo(name="Milton", category=3, lat=26.0, lon=-83.0, wind_mph=120)
        assert evaluator.evaluate(storm) == ThreatLevel.CRITICAL

    def test_medium_distance_cat1_is_medium(self):
        evaluator = ThreatEvaluator(target_lat=27.95, target_lon=-82.46)
        storm = StormInfo(name="Weak", category=1, lat=24.0, lon=-80.0, wind_mph=75)
        level = evaluator.evaluate(storm)
        assert level in (ThreatLevel.LOW, ThreatLevel.MEDIUM)

class TestNOAAClient:
    @pytest.fixture
    def client(self):
        return NOAAClient()

    async def test_parse_active_storms(self, client):
        mock_geojson = {
            "features": [
                {
                    "properties": {
                        "name": "MILTON",
                        "ssCategory": 3,
                        "maxSustainedWind": 120,
                    },
                    "geometry": {"coordinates": [-83.0, 26.0]},
                }
            ]
        }
        with patch.object(client, "_fetch", new_callable=AsyncMock, return_value=mock_geojson):
            storms = await client.get_active_storms()
            assert len(storms) == 1
            assert storms[0].name == "MILTON"
            assert storms[0].category == 3

    async def test_api_failure_returns_empty(self, client):
        with patch.object(client, "_fetch", new_callable=AsyncMock, side_effect=Exception("timeout")):
            storms = await client.get_active_storms()
            assert storms == []
