import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from backend.ml.data_collector import (
    EIAClient,
    WeatherClient,
    GridDataPoint,
    WeatherDataPoint,
    DataQuality,
)


class TestEIAClient:
    @pytest.fixture
    def client(self):
        return EIAClient(api_key="test-key")

    async def test_parse_valid_response(self, client):
        mock_response = {
            "response": {
                "data": [
                    {
                        "period": "2026-04-13T14:00",
                        "value": 8420,
                        "type-name": "Demand",
                    }
                ]
            }
        }
        with patch.object(client, "_fetch", new_callable=AsyncMock, return_value=mock_response):
            points = await client.get_hourly_demand("FPC", hours=24)
            assert len(points) == 1
            assert points[0].demand_mw == 8420
            assert points[0].quality == DataQuality.GOOD

    async def test_null_value_uses_fallback(self, client):
        mock_response = {
            "response": {"data": [{"period": "2026-04-13T14:00", "value": None, "type-name": "Demand"}]}
        }
        with patch.object(client, "_fetch", new_callable=AsyncMock, return_value=mock_response):
            points = await client.get_hourly_demand("FPC", hours=24)
            assert points[0].demand_mw == 0
            assert points[0].quality == DataQuality.FALLBACK


class TestWeatherClient:
    @pytest.fixture
    def client(self):
        return WeatherClient(api_key="test-key")

    async def test_parse_valid_forecast(self, client):
        mock_response = {
            "list": [
                {
                    "dt": 1681387200,
                    "main": {"temp": 307.15, "humidity": 65},
                    "clouds": {"all": 20},
                    "wind": {"speed": 4.5},
                }
            ]
        }
        with patch.object(client, "_fetch", new_callable=AsyncMock, return_value=mock_response):
            points = await client.get_forecast(lat=27.9506, lon=-82.4572)
            assert len(points) == 1
            assert points[0].temperature_f == pytest.approx(93.2, abs=0.1)
            assert points[0].humidity == 65

    async def test_api_failure_returns_empty_with_error_quality(self, client):
        with patch.object(client, "_fetch", new_callable=AsyncMock, side_effect=Exception("timeout")):
            points = await client.get_forecast(lat=27.9506, lon=-82.4572)
            assert points == []
