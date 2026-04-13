from __future__ import annotations

import enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import httpx


class DataQuality(str, enum.Enum):
    GOOD = "good"
    STALE = "stale"
    FALLBACK = "fallback"
    ERROR = "error"


class GridDataPoint(BaseModel):
    timestamp: datetime
    demand_mw: float = Field(ge=0)
    quality: DataQuality = DataQuality.GOOD


class WeatherDataPoint(BaseModel):
    timestamp: datetime
    temperature_f: float
    humidity: float = Field(ge=0, le=100)
    cloud_cover: float = Field(ge=0, le=100)
    wind_speed_mph: float = Field(ge=0)
    quality: DataQuality = DataQuality.GOOD


class EIAClient:
    BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._http = httpx.AsyncClient(timeout=30)

    async def _fetch(self, params: dict) -> dict:
        params["api_key"] = self.api_key
        resp = await self._http.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_hourly_demand(self, region: str = "FPC", hours: int = 48) -> list[GridDataPoint]:
        try:
            data = await self._fetch({
                "frequency": "hourly",
                "data[0]": "value",
                "facets[respondent][]": region,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": hours,
            })
        except Exception:
            return []

        points = []
        for row in data.get("response", {}).get("data", []):
            value = row.get("value")
            quality = DataQuality.GOOD
            if value is None:
                value = 0
                quality = DataQuality.FALLBACK
            points.append(GridDataPoint(
                timestamp=datetime.fromisoformat(row["period"]).replace(tzinfo=timezone.utc),
                demand_mw=float(value),
                quality=quality,
            ))
        return points

    async def close(self):
        await self._http.aclose()


class WeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._http = httpx.AsyncClient(timeout=30)

    async def _fetch(self, params: dict) -> dict:
        params["appid"] = self.api_key
        resp = await self._http.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_forecast(self, lat: float, lon: float) -> list[WeatherDataPoint]:
        try:
            data = await self._fetch({"lat": lat, "lon": lon, "units": "standard"})
        except Exception:
            return []

        points = []
        for item in data.get("list", []):
            kelvin = item["main"]["temp"]
            fahrenheit = (kelvin - 273.15) * 9 / 5 + 32
            points.append(WeatherDataPoint(
                timestamp=datetime.fromtimestamp(item["dt"], tz=timezone.utc),
                temperature_f=round(fahrenheit, 1),
                humidity=item["main"]["humidity"],
                cloud_cover=item["clouds"]["all"],
                wind_speed_mph=item["wind"]["speed"] * 2.237,
                quality=DataQuality.GOOD,
            ))
        return points

    async def close(self):
        await self._http.aclose()
