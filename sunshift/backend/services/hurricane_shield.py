# backend/services/hurricane_shield.py
from __future__ import annotations
import enum, math
from dataclasses import dataclass, field
import httpx


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


class ThreatLevel(str, enum.Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StormInfo:
    name: str
    category: int
    lat: float
    lon: float
    wind_mph: float


class ThreatEvaluator:
    def __init__(self, target_lat: float = 27.9506, target_lon: float = -82.4572):
        self.target_lat = target_lat
        self.target_lon = target_lon

    def evaluate(self, storm: StormInfo) -> ThreatLevel:
        dist = haversine_km(self.target_lat, self.target_lon, storm.lat, storm.lon)
        if dist > 1000: return ThreatLevel.NONE
        if dist > 500: return ThreatLevel.LOW if storm.category < 3 else ThreatLevel.MEDIUM
        if dist > 250: return ThreatLevel.MEDIUM if storm.category < 3 else ThreatLevel.HIGH
        return ThreatLevel.HIGH if storm.category < 2 else ThreatLevel.CRITICAL


class NOAAClient:
    URL = "https://www.nhc.noaa.gov/CurrentSurges.json"
    ACTIVE_URL = "https://www.nhc.noaa.gov/gis/forecast/archive/"

    def __init__(self):
        self._http = httpx.AsyncClient(timeout=30)

    async def _fetch(self, url: str) -> dict:
        resp = await self._http.get(url)
        resp.raise_for_status()
        return resp.json()

    async def get_active_storms(self) -> list[StormInfo]:
        try:
            data = await self._fetch("https://www.nhc.noaa.gov/CurrentSurges.json")
        except Exception:
            return []
        storms = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [0, 0])
            storms.append(StormInfo(
                name=props.get("name", "Unknown"),
                category=props.get("ssCategory", 0),
                lat=coords[1], lon=coords[0],
                wind_mph=props.get("maxSustainedWind", 0),
            ))
        return storms

    async def close(self):
        await self._http.aclose()


@dataclass
class ShieldStatus:
    shield_mode: str = "standby"  # "standby" | "active"
    active_threats: int = 0
    storms: list[StormInfo] = field(default_factory=list)
    max_threat_level: ThreatLevel = ThreatLevel.NONE
    last_check: str = ""
    alert_message: str = ""


class ShieldOrchestrator:
    def __init__(self) -> None:
        self.noaa_client = NOAAClient()
        self.evaluator = ThreatEvaluator()
        self.status = ShieldStatus()
        self._demo_mode = False

    async def check(self) -> ShieldStatus:
        from datetime import datetime, timezone

        if self._demo_mode:
            return self._demo_status()

        storms = await self.noaa_client.get_active_storms()
        threat_levels = [(s, self.evaluator.evaluate(s)) for s in storms]

        active_threats = sum(1 for _, level in threat_levels if level.value not in ("none", "low"))
        max_level = max(
            (level for _, level in threat_levels),
            default=ThreatLevel.NONE,
            key=lambda x: list(ThreatLevel).index(x),
        )

        self.status = ShieldStatus(
            shield_mode="active" if max_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL) else "standby",
            active_threats=active_threats,
            storms=storms,
            max_threat_level=max_level,
            last_check=datetime.now(timezone.utc).isoformat(),
        )
        return self.status

    def activate_demo(self) -> None:
        self._demo_mode = True

    def deactivate_demo(self) -> None:
        self._demo_mode = False
        self.status = ShieldStatus()

    def _demo_status(self) -> ShieldStatus:
        from datetime import datetime, timezone

        return ShieldStatus(
            shield_mode="active",
            active_threats=1,
            storms=[StormInfo(name="DEMO-STORM", category=3, lat=26.0, lon=-83.0, wind_mph=120)],
            max_threat_level=ThreatLevel.CRITICAL,
            last_check=datetime.now(timezone.utc).isoformat(),
            alert_message=(
                "[DEMO] Category 3 hurricane approaching Tampa Bay. "
                "Hurricane Shield activated — all data being backed up to AWS Ohio."
            ),
        )
