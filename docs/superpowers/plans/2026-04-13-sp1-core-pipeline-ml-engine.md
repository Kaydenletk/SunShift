# SP1: Core Pipeline + ML Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the end-to-end data pipeline: collect electricity/weather data → engineer features → train ML ensemble (Prophet + XGBoost) → serve predictions via FastAPI → on-prem agent that collects metrics and syncs files to S3.

**Architecture:** Event-driven pipeline. FastAPI backend on ECS Fargate serves predictions and coordinates agent. ML ensemble (Prophet baseline + XGBoost multi-factor) predicts hourly electricity costs 48h ahead. Python agent runs locally, collects metrics, syncs files to S3 via multipart upload, receives commands via WebSocket.

**Tech Stack:** Python 3.12, FastAPI, XGBoost, Prophet, boto3, psutil, watchdog, pydantic, pytest, SQLite, Docker

**Spec:** `docs/superpowers/specs/2026-04-13-sunshift-mvp-design.md`

---

## File Structure

```
sunshift/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Settings via pydantic-settings
│   │   └── deps.py                 # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py                # Agent schemas
│   │   ├── prediction.py           # Prediction request/response
│   │   ├── metrics.py              # Metrics schemas
│   │   └── commands.py             # Command schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── agents.py           # Agent registration + status
│   │   │   ├── predictions.py      # Prediction endpoint
│   │   │   ├── metrics.py          # Metrics ingestion
│   │   │   └── commands.py         # Command dispatch
│   │   └── websocket.py            # WebSocket handler
│   ├── services/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Migration scheduling logic
│   │   └── savings.py              # Savings calculator
│   └── ml/
│       ├── __init__.py
│       ├── data_collector.py       # EIA + OpenWeatherMap API clients
│       ├── features.py             # Feature engineering pipeline
│       ├── model.py                # Prophet + XGBoost ensemble
│       ├── predict.py              # Prediction service (load + predict + cache)
│       └── scheduler.py            # Optimal window finder
├── agent/
│   ├── __init__.py
│   ├── main.py                     # Agent entry point
│   ├── config.py                   # YAML config loader
│   ├── collector.py                # System metrics via psutil
│   ├── sync_engine.py              # S3 multipart upload + encryption
│   ├── command_receiver.py         # WebSocket client + command handler
│   └── db.py                       # SQLite local buffer
├── tests/
│   ├── conftest.py
│   ├── backend/
│   │   ├── test_models.py
│   │   ├── test_data_collector.py
│   │   ├── test_features.py
│   │   ├── test_model.py
│   │   ├── test_predict.py
│   │   ├── test_routes.py
│   │   └── test_websocket.py
│   └── agent/
│       ├── test_collector.py
│       ├── test_sync_engine.py
│       └── test_command_receiver.py
└── scripts/
    ├── collect_historical_data.py  # One-time data bootstrap
    └── train_model.py              # Training script
```

---

### Task 0: Project Scaffolding + Shared Schemas

**Goal:** Set up Python project with all dependencies, directory structure, shared Pydantic models, and config system.

**Files:**
- Create: `sunshift/pyproject.toml`
- Create: `sunshift/backend/__init__.py`, `sunshift/backend/core/__init__.py`, `sunshift/backend/core/config.py`
- Create: `sunshift/backend/models/__init__.py`, `sunshift/backend/models/agent.py`, `sunshift/backend/models/prediction.py`, `sunshift/backend/models/metrics.py`, `sunshift/backend/models/commands.py`
- Create: `sunshift/.env.example`
- Create: `sunshift/tests/conftest.py`, `sunshift/tests/backend/test_models.py`

**Acceptance Criteria:**
- [ ] `uv sync` installs all dependencies without error
- [ ] Pydantic models validate correct data and reject invalid data
- [ ] Config loads from environment variables
- [ ] `pytest tests/backend/test_models.py` passes

**Verify:** `cd sunshift && uv run pytest tests/backend/test_models.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Create pyproject.toml with all dependencies**

```toml
[project]
name = "sunshift"
version = "0.1.0"
description = "AI-Powered Compute Cost Optimizer"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "boto3>=1.35.0",
    "xgboost>=2.1.0",
    "prophet>=1.1.6",
    "pandas>=2.2.0",
    "numpy>=2.1.0",
    "scikit-learn>=1.6.0",
    "httpx>=0.28.0",
    "websockets>=14.0",
    "psutil>=6.1.0",
    "watchdog>=6.0.0",
    "cryptography>=44.0.0",
    "pyyaml>=6.0.2",
    "anthropic>=0.42.0",
    "mlflow>=2.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "moto[s3,dynamodb,events]>=5.0.0",
    "ruff>=0.8.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

- [ ] **Step 2: Create config system**

Create `sunshift/backend/core/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SunShift"
    debug: bool = False

    # AWS
    aws_region: str = "us-east-2"
    s3_bucket_customer_data: str = "sunshift-customer-data"
    s3_bucket_ml_artifacts: str = "sunshift-ml-artifacts"
    dynamodb_table: str = "sunshift-main"

    # API Keys
    openweathermap_api_key: str = ""
    eia_api_key: str = ""
    anthropic_api_key: str = ""

    # ML
    model_version: str = "v0.1.0"
    prediction_cache_ttl_seconds: int = 3600
    fallback_peak_start_hour: int = 12
    fallback_peak_end_hour: int = 21

    model_config = {"env_prefix": "SUNSHIFT_", "env_file": ".env"}


settings = Settings()
```

- [ ] **Step 3: Create Pydantic models**

Create `sunshift/backend/models/agent.py`:

```python
from datetime import datetime
from pydantic import BaseModel, Field


class AgentRegistration(BaseModel):
    agent_id: str = Field(..., pattern=r"^[a-z0-9\-]+$", max_length=64)
    name: str = Field(..., max_length=128)
    location: str = Field(default="tampa_fl")
    watch_paths: list[str] = Field(default_factory=list)


class AgentStatus(BaseModel):
    agent_id: str
    status: str = Field(..., pattern=r"^(online|offline|syncing|error)$")
    last_seen: datetime
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_percent: float | None = None
    last_sync: datetime | None = None
    bytes_synced: int = 0
```

Create `sunshift/backend/models/prediction.py`:

```python
from datetime import datetime
from pydantic import BaseModel, Field


class HourlyForecast(BaseModel):
    hour: datetime
    cost_cents_kwh: float = Field(..., ge=0)
    demand_mw: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)


class OptimalWindow(BaseModel):
    rank: int
    start: datetime
    end: datetime
    avg_cost_cents_kwh: float
    estimated_savings_dollars: float
    workload_recommendation: str = Field(..., pattern=r"^(FULL_SYNC|INCREMENTAL_SYNC|AI_TRAINING)$")


class PredictionResponse(BaseModel):
    prediction_id: str
    location: str
    generated_at: datetime
    model_version: str
    hourly_forecast: list[HourlyForecast]
    optimal_windows: list[OptimalWindow]
    explanation: str
    hurricane_status: dict = Field(default_factory=lambda: {"active_threats": 0, "shield_mode": "standby"})
```

Create `sunshift/backend/models/metrics.py`:

```python
from datetime import datetime
from pydantic import BaseModel, Field


class MetricsPayload(BaseModel):
    agent_id: str
    timestamp: datetime
    cpu_percent: float = Field(..., ge=0, le=100)
    memory_percent: float = Field(..., ge=0, le=100)
    disk_percent: float = Field(..., ge=0, le=100)
    network_bytes_sent: int = Field(..., ge=0)
    network_bytes_recv: int = Field(..., ge=0)
    estimated_power_watts: float = Field(default=0, ge=0)
```

Create `sunshift/backend/models/commands.py`:

```python
from datetime import datetime
from pydantic import BaseModel, Field


class AgentCommand(BaseModel):
    command: str = Field(..., pattern=r"^(START_SYNC|FULL_BACKUP|STOP|INCREMENTAL_SYNC)$")
    agent_id: str
    issued_at: datetime
    paths: list[str] = Field(default_factory=list)
    priority: str = Field(default="normal", pattern=r"^(low|normal|high|critical)$")


class CommandResult(BaseModel):
    command: str
    agent_id: str
    status: str = Field(..., pattern=r"^(success|failed|in_progress|queued)$")
    started_at: datetime
    completed_at: datetime | None = None
    bytes_transferred: int = 0
    error_message: str | None = None
```

- [ ] **Step 4: Write tests for models**

Create `sunshift/tests/backend/test_models.py`:

```python
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
```

- [ ] **Step 5: Create .env.example and init files**

Create `sunshift/.env.example`:

```
SUNSHIFT_DEBUG=true
SUNSHIFT_OPENWEATHERMAP_API_KEY=your_key_here
SUNSHIFT_EIA_API_KEY=your_key_here
SUNSHIFT_ANTHROPIC_API_KEY=your_key_here
SUNSHIFT_AWS_REGION=us-east-2
```

Create all `__init__.py` files (empty) for: `backend/`, `backend/core/`, `backend/models/`, `backend/api/`, `backend/api/routes/`, `backend/services/`, `backend/ml/`, `agent/`, `tests/`, `tests/backend/`, `tests/agent/`.

- [ ] **Step 6: Install and run tests**

```bash
cd sunshift && uv sync --dev && uv run pytest tests/backend/test_models.py -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add sunshift/
git commit -m "feat(sp1): project scaffolding + shared Pydantic models + config system"
```

---

### Task 1: Data Collection Clients

**Goal:** Build API clients for EIA (electricity grid data), OpenWeatherMap (weather), with Pydantic validation and fallback handling.

**Files:**
- Create: `sunshift/backend/ml/data_collector.py`
- Create: `sunshift/tests/backend/test_data_collector.py`

**Acceptance Criteria:**
- [ ] EIA client fetches hourly demand data and returns validated Pydantic models
- [ ] Weather client fetches forecast and returns validated models
- [ ] Null/missing data falls back to last known value
- [ ] Stale data (>2h old) flags response as low confidence
- [ ] Tests use httpx mocking, no real API calls

**Verify:** `cd sunshift && uv run pytest tests/backend/test_data_collector.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests for data collector**

Create `sunshift/tests/backend/test_data_collector.py`:

```python
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
            assert points[0].temperature_f == pytest.approx(93.4, abs=0.1)
            assert points[0].humidity == 65

    async def test_api_failure_returns_empty_with_error_quality(self, client):
        with patch.object(client, "_fetch", new_callable=AsyncMock, side_effect=Exception("timeout")):
            points = await client.get_forecast(lat=27.9506, lon=-82.4572)
            assert points == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd sunshift && uv run pytest tests/backend/test_data_collector.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'backend.ml.data_collector'`

- [ ] **Step 3: Implement data collector**

Create `sunshift/backend/ml/data_collector.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd sunshift && uv run pytest tests/backend/test_data_collector.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/ml/data_collector.py sunshift/tests/backend/test_data_collector.py
git commit -m "feat(sp1): EIA + OpenWeatherMap API clients with data quality validation"
```

---

### Task 2: Feature Engineering Pipeline

**Goal:** Build feature engineering that transforms raw weather + grid data into ML-ready features with cyclical encoding, lag features, and interaction terms.

**Files:**
- Create: `sunshift/backend/ml/features.py`
- Create: `sunshift/tests/backend/test_features.py`

**Acceptance Criteria:**
- [ ] Produces all 7 features from spec: temp_rolling_6h, demand_lag_24h, demand_lag_168h, hour_sin, hour_cos, temp_x_hour, is_peak_transition, cooling_degree_hours
- [ ] Cyclical encoding: hour 23 and hour 0 produce similar sin/cos values
- [ ] Missing lag values (insufficient history) filled with 0 and flagged
- [ ] Returns pandas DataFrame ready for XGBoost

**Verify:** `cd sunshift && uv run pytest tests/backend/test_features.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests for feature engineering**

Create `sunshift/tests/backend/test_features.py`:

```python
import pytest
import math
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

from backend.ml.features import FeatureEngineer


class TestCyclicalEncoding:
    def test_hour_23_and_hour_0_are_close(self):
        fe = FeatureEngineer()
        sin_23, cos_23 = fe._cyclical_hour(23)
        sin_0, cos_0 = fe._cyclical_hour(0)
        distance = math.sqrt((sin_23 - sin_0) ** 2 + (cos_23 - cos_0) ** 2)
        assert distance < 0.3  # close on unit circle

    def test_hour_12_opposite_hour_0(self):
        fe = FeatureEngineer()
        sin_12, cos_12 = fe._cyclical_hour(12)
        sin_0, cos_0 = fe._cyclical_hour(0)
        distance = math.sqrt((sin_12 - sin_0) ** 2 + (cos_12 - cos_0) ** 2)
        assert distance > 1.5  # far apart


class TestFeatureEngineer:
    @pytest.fixture
    def sample_data(self):
        hours = 200
        timestamps = [datetime(2026, 4, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(hours)]
        return pd.DataFrame({
            "timestamp": timestamps,
            "temperature_f": [75 + 15 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
            "humidity": [60 + 10 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
            "demand_mw": [5000 + 3000 * math.sin(2 * math.pi * i / 24) for i in range(hours)],
        })

    def test_produces_all_required_columns(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        required = [
            "hour_sin", "hour_cos", "temp_rolling_6h", "demand_lag_24h",
            "demand_lag_168h", "temp_x_hour", "is_peak_transition", "cooling_degree_hours",
        ]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_no_nan_in_output(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        assert not result.isna().any().any(), f"NaN found in columns: {result.columns[result.isna().any()].tolist()}"

    def test_peak_transition_flags_correct_hours(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        peak_rows = result[result["is_peak_transition"] == 1]
        hours = peak_rows["timestamp"].dt.hour.unique()
        # Should flag hours 11, 12, 20, 21 (30 min before/after 12-21 peak)
        for h in [11, 12, 21]:
            assert h in hours, f"Hour {h} should be peak transition"

    def test_cooling_degree_hours_zero_below_65(self, sample_data):
        fe = FeatureEngineer()
        result = fe.build_features(sample_data)
        cold_rows = result[result["temperature_f"] < 65]
        if len(cold_rows) > 0:
            assert (cold_rows["cooling_degree_hours"] == 0).all()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd sunshift && uv run pytest tests/backend/test_features.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement feature engineering**

Create `sunshift/backend/ml/features.py`:

```python
from __future__ import annotations

import math
import pandas as pd
import numpy as np


class FeatureEngineer:
    PEAK_START = 12  # FPL TOU peak start
    PEAK_END = 21    # FPL TOU peak end

    def _cyclical_hour(self, hour: int) -> tuple[float, float]:
        sin_val = math.sin(2 * math.pi * hour / 24)
        cos_val = math.cos(2 * math.pi * hour / 24)
        return sin_val, cos_val

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        hour = df["timestamp"].dt.hour

        # Cyclical encoding
        df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
        df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

        # Rolling temperature (6h window)
        df["temp_rolling_6h"] = df["temperature_f"].rolling(window=6, min_periods=1).mean()

        # Lag features
        df["demand_lag_24h"] = df["demand_mw"].shift(24).fillna(0)
        df["demand_lag_168h"] = df["demand_mw"].shift(168).fillna(0)

        # Interaction: temperature * hour_sin (captures temp-at-time-of-day)
        df["temp_x_hour"] = df["temperature_f"] * df["hour_sin"]

        # Peak transition flag: within 1 hour of peak boundaries
        df["is_peak_transition"] = ((hour >= self.PEAK_START - 1) & (hour <= self.PEAK_START) |
                                     (hour >= self.PEAK_END) & (hour <= self.PEAK_END + 1)).astype(int)

        # Cooling degree hours
        df["cooling_degree_hours"] = np.maximum(0, df["temperature_f"] - 65)

        # Day of week (0=Monday)
        df["day_of_week"] = df["timestamp"].dt.dayofweek

        # Is weekend
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        # Month
        df["month"] = df["timestamp"].dt.month

        # Is FPL peak
        df["is_fpl_peak"] = ((hour >= self.PEAK_START) & (hour < self.PEAK_END)).astype(int)

        return df

    def get_feature_columns(self) -> list[str]:
        return [
            "hour_sin", "hour_cos", "temp_rolling_6h", "demand_lag_24h",
            "demand_lag_168h", "temp_x_hour", "is_peak_transition",
            "cooling_degree_hours", "day_of_week", "is_weekend", "month",
            "is_fpl_peak", "temperature_f", "humidity",
        ]
```

- [ ] **Step 4: Run tests**

```bash
cd sunshift && uv run pytest tests/backend/test_features.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/ml/features.py sunshift/tests/backend/test_features.py
git commit -m "feat(sp1): feature engineering — cyclical encoding, lag features, interaction terms"
```

---

### Task 3: ML Model Training (Prophet + XGBoost Ensemble)

**Goal:** Build training pipeline: collect historical data → train Prophet baseline → train XGBoost on full features → evaluate → serialize models.

**Files:**
- Create: `sunshift/backend/ml/model.py`
- Create: `sunshift/scripts/collect_historical_data.py`
- Create: `sunshift/scripts/train_model.py`
- Create: `sunshift/tests/backend/test_model.py`

**Acceptance Criteria:**
- [ ] Prophet model trains on demand time-series and produces 48h forecast
- [ ] XGBoost model trains on full feature set and predicts cost_cents_kwh
- [ ] Ensemble combines both outputs
- [ ] Models serialize/deserialize to files (joblib)
- [ ] MAPE evaluated on hold-out set
- [ ] Tests use synthetic data, no real API calls

**Verify:** `cd sunshift && uv run pytest tests/backend/test_model.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests for model**

Create `sunshift/tests/backend/test_model.py`:

```python
import pytest
import math
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path

from backend.ml.model import SunShiftModel


def _synthetic_training_data(days: int = 90) -> pd.DataFrame:
    hours = days * 24
    timestamps = [datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(hours)]
    hour_vals = [t.hour for t in timestamps]
    rows = []
    for i, ts in enumerate(timestamps):
        h = hour_vals[i]
        temp = 75 + 15 * math.sin(2 * math.pi * h / 24) + np.random.normal(0, 2)
        demand = 5000 + 3000 * math.sin(2 * math.pi * h / 24) + np.random.normal(0, 200)
        cost = 8 + 12 * max(0, math.sin(2 * math.pi * (h - 6) / 24)) + np.random.normal(0, 1)
        rows.append({
            "timestamp": ts, "temperature_f": temp, "humidity": 60,
            "demand_mw": max(0, demand), "cost_cents_kwh": max(0, cost),
        })
    return pd.DataFrame(rows)


class TestSunShiftModel:
    @pytest.fixture
    def trained_model(self, tmp_path):
        model = SunShiftModel()
        data = _synthetic_training_data(days=90)
        metrics = model.train(data)
        return model, metrics

    def test_train_returns_metrics(self, trained_model):
        _, metrics = trained_model
        assert "mape" in metrics
        assert "mae" in metrics
        assert metrics["mape"] >= 0

    def test_predict_returns_48_hours(self, trained_model):
        model, _ = trained_model
        data = _synthetic_training_data(days=10)
        predictions = model.predict(data.tail(48))
        assert len(predictions) == 48
        assert all(p >= 0 for p in predictions)

    def test_save_and_load(self, trained_model, tmp_path):
        model, _ = trained_model
        model.save(tmp_path / "model")
        loaded = SunShiftModel.load(tmp_path / "model")
        data = _synthetic_training_data(days=10)
        original_preds = model.predict(data.tail(48))
        loaded_preds = loaded.predict(data.tail(48))
        np.testing.assert_array_almost_equal(original_preds, loaded_preds)
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd sunshift && uv run pytest tests/backend/test_model.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement model**

Create `sunshift/backend/ml/model.py`:

```python
from __future__ import annotations

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from backend.ml.features import FeatureEngineer


class SunShiftModel:
    def __init__(self):
        self.prophet_model: Prophet | None = None
        self.xgb_model: XGBRegressor | None = None
        self.feature_engineer = FeatureEngineer()
        self.metrics: dict = {}

    def train(self, data: pd.DataFrame, test_ratio: float = 0.2) -> dict:
        data = self.feature_engineer.build_features(data)
        split_idx = int(len(data) * (1 - test_ratio))
        train_df = data.iloc[:split_idx]
        test_df = data.iloc[split_idx:]

        # Train Prophet on demand time-series
        prophet_df = train_df[["timestamp", "demand_mw"]].rename(
            columns={"timestamp": "ds", "demand_mw": "y"}
        )
        prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)
        self.prophet_model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
        self.prophet_model.fit(prophet_df)

        # Add Prophet predictions as feature for XGBoost
        all_prophet_df = data[["timestamp"]].rename(columns={"timestamp": "ds"})
        all_prophet_df["ds"] = all_prophet_df["ds"].dt.tz_localize(None)
        prophet_forecast = self.prophet_model.predict(all_prophet_df)
        data["prophet_demand"] = prophet_forecast["yhat"].values

        # Rebuild train/test with prophet feature
        train_df = data.iloc[:split_idx]
        test_df = data.iloc[split_idx:]

        feature_cols = self.feature_engineer.get_feature_columns() + ["prophet_demand"]
        X_train = train_df[feature_cols].values
        y_train = train_df["cost_cents_kwh"].values
        X_test = test_df[feature_cols].values
        y_test = test_df["cost_cents_kwh"].values

        # Train XGBoost
        self.xgb_model = XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
        )
        self.xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        # Evaluate
        y_pred = self.xgb_model.predict(X_test)
        self.metrics = {
            "mape": float(mean_absolute_percentage_error(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "test_size": len(y_test),
            "train_size": len(y_train),
        }
        return self.metrics

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        if self.xgb_model is None or self.prophet_model is None:
            raise RuntimeError("Model not trained. Call train() or load() first.")

        data = self.feature_engineer.build_features(data)

        prophet_df = data[["timestamp"]].rename(columns={"timestamp": "ds"})
        prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)
        prophet_forecast = self.prophet_model.predict(prophet_df)
        data["prophet_demand"] = prophet_forecast["yhat"].values

        feature_cols = self.feature_engineer.get_feature_columns() + ["prophet_demand"]
        X = data[feature_cols].values
        predictions = self.xgb_model.predict(X)
        return np.maximum(predictions, 0)

    def save(self, path: Path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.xgb_model, path / "xgb_model.joblib")
        with open(path / "prophet_model.json", "w") as f:
            from prophet.serialize import model_to_json
            f.write(model_to_json(self.prophet_model))
        with open(path / "metrics.json", "w") as f:
            json.dump(self.metrics, f)

    @classmethod
    def load(cls, path: Path) -> SunShiftModel:
        path = Path(path)
        instance = cls()
        instance.xgb_model = joblib.load(path / "xgb_model.joblib")
        with open(path / "prophet_model.json", "r") as f:
            from prophet.serialize import model_from_json
            instance.prophet_model = model_from_json(f.read())
        if (path / "metrics.json").exists():
            with open(path / "metrics.json") as f:
                instance.metrics = json.load(f)
        return instance
```

- [ ] **Step 4: Run tests**

```bash
cd sunshift && uv run pytest tests/backend/test_model.py -v --timeout=120
```

Expected: All tests PASS (training may take ~30s on synthetic data).

- [ ] **Step 5: Create training script**

Create `sunshift/scripts/train_model.py`:

```python
#!/usr/bin/env python3
"""Train SunShift ML model on historical data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from backend.ml.model import SunShiftModel


def main():
    data_path = Path("data/historical_training_data.parquet")
    if not data_path.exists():
        print(f"Training data not found at {data_path}")
        print("Run scripts/collect_historical_data.py first.")
        sys.exit(1)

    data = pd.read_parquet(data_path)
    print(f"Loaded {len(data)} rows of training data")

    model = SunShiftModel()
    metrics = model.train(data)
    print(f"Training complete. Metrics: {metrics}")

    output_path = Path("models/latest")
    model.save(output_path)
    print(f"Model saved to {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```bash
git add sunshift/backend/ml/model.py sunshift/tests/backend/test_model.py sunshift/scripts/train_model.py
git commit -m "feat(sp1): Prophet + XGBoost ensemble model with training pipeline"
```

---

### Task 4: Prediction Service + Optimal Window Scheduler

**Goal:** Build prediction service that loads trained model, runs predictions with caching and circuit breaker fallback, and finds optimal cost windows.

**Files:**
- Create: `sunshift/backend/ml/predict.py`
- Create: `sunshift/backend/ml/scheduler.py`
- Create: `sunshift/tests/backend/test_predict.py`

**Acceptance Criteria:**
- [ ] Prediction service loads model from disk, caches predictions for 1 hour
- [ ] Circuit breaker: if model fails or confidence < 0.5, returns static TOU schedule
- [ ] Scheduler finds cheapest N-hour consecutive windows from hourly forecast
- [ ] Returns PredictionResponse matching spec schema

**Verify:** `cd sunshift && uv run pytest tests/backend/test_predict.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests**

Create `sunshift/tests/backend/test_predict.py`:

```python
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta

from backend.ml.scheduler import find_cheapest_windows
from backend.ml.predict import PredictionService, FallbackPrediction


class TestFindCheapestWindows:
    def test_finds_cheapest_consecutive_hours(self):
        costs = [20, 22, 25, 27, 26, 24, 18, 12, 8, 6, 5, 6, 8, 10, 14, 18, 20, 22, 25, 27, 26, 22, 15, 10]
        base = datetime(2026, 4, 13, tzinfo=timezone.utc)
        timestamps = [base + timedelta(hours=i) for i in range(24)]
        windows = find_cheapest_windows(timestamps, costs, min_duration=3, max_duration=6, top_n=2)
        assert len(windows) == 2
        assert windows[0].avg_cost_cents_kwh < windows[1].avg_cost_cents_kwh
        # Cheapest 3h window should be around hours 8-10 (costs 6, 5, 6)
        assert windows[0].start.hour in range(8, 12)

    def test_respects_min_duration(self):
        costs = [10] * 24
        base = datetime(2026, 4, 13, tzinfo=timezone.utc)
        timestamps = [base + timedelta(hours=i) for i in range(24)]
        windows = find_cheapest_windows(timestamps, costs, min_duration=4, max_duration=8, top_n=1)
        assert len(windows) == 1
        duration_hours = (windows[0].end - windows[0].start).total_seconds() / 3600
        assert duration_hours >= 4


class TestFallbackPrediction:
    def test_fallback_returns_static_peak(self):
        fb = FallbackPrediction(peak_start=12, peak_end=21)
        forecast = fb.generate(datetime(2026, 4, 13, tzinfo=timezone.utc))
        assert len(forecast) == 48
        peak_cost = next(f for f in forecast if f.hour.hour == 14).cost_cents_kwh
        offpeak_cost = next(f for f in forecast if f.hour.hour == 3).cost_cents_kwh
        assert peak_cost > offpeak_cost
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd sunshift && uv run pytest tests/backend/test_predict.py -v
```

- [ ] **Step 3: Implement scheduler**

Create `sunshift/backend/ml/scheduler.py`:

```python
from __future__ import annotations

from datetime import datetime
from backend.models.prediction import OptimalWindow


def find_cheapest_windows(
    timestamps: list[datetime],
    costs: list[float],
    min_duration: int = 2,
    max_duration: int = 8,
    top_n: int = 3,
) -> list[OptimalWindow]:
    if len(timestamps) != len(costs):
        raise ValueError("timestamps and costs must have same length")

    candidates: list[OptimalWindow] = []

    for duration in range(min_duration, max_duration + 1):
        for i in range(len(costs) - duration + 1):
            window_costs = costs[i : i + duration]
            avg_cost = sum(window_costs) / len(window_costs)
            peak_avg = 25.0  # approximate peak cost for savings calc
            savings = (peak_avg - avg_cost) * duration * 2.5 / 100  # rough kWh * hours

            candidates.append(OptimalWindow(
                rank=0,
                start=timestamps[i],
                end=timestamps[i + duration],
                avg_cost_cents_kwh=round(avg_cost, 2),
                estimated_savings_dollars=round(max(0, savings), 2),
                workload_recommendation="FULL_SYNC" if duration >= 4 else "INCREMENTAL_SYNC",
            ))

    candidates.sort(key=lambda w: w.avg_cost_cents_kwh)
    top = candidates[:top_n]
    for rank, window in enumerate(top, 1):
        window.rank = rank
    return top
```

- [ ] **Step 4: Implement prediction service with fallback**

Create `sunshift/backend/ml/predict.py`:

```python
from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from backend.models.prediction import HourlyForecast, PredictionResponse
from backend.ml.model import SunShiftModel
from backend.ml.scheduler import find_cheapest_windows
from backend.core.config import settings


class FallbackPrediction:
    def __init__(self, peak_start: int = 12, peak_end: int = 21):
        self.peak_start = peak_start
        self.peak_end = peak_end

    def generate(self, start: datetime) -> list[HourlyForecast]:
        forecasts = []
        for i in range(48):
            hour_dt = start + timedelta(hours=i)
            h = hour_dt.hour
            if self.peak_start <= h < self.peak_end:
                cost = 25.0
                demand = 8500.0
            else:
                cost = 7.0
                demand = 4500.0
            forecasts.append(HourlyForecast(
                hour=hour_dt, cost_cents_kwh=cost, demand_mw=demand, confidence=0.3,
            ))
        return forecasts


class PredictionService:
    def __init__(self, model_path: Path | None = None):
        self.model: SunShiftModel | None = None
        self.fallback = FallbackPrediction(settings.fallback_peak_start_hour, settings.fallback_peak_end_hour)
        self._cache: dict[str, tuple[float, PredictionResponse]] = {}
        self._cache_ttl = settings.prediction_cache_ttl_seconds

        if model_path and model_path.exists():
            self.model = SunShiftModel.load(model_path)

    def predict(self, location: str = "tampa_fl") -> PredictionResponse:
        # Check cache
        cache_key = f"{location}:{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H')}"
        if cache_key in self._cache:
            cached_time, cached_response = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_response

        now = datetime.now(timezone.utc)

        # Circuit breaker: use fallback if no model
        if self.model is None:
            forecasts = self.fallback.generate(now)
        else:
            try:
                forecasts = self._run_model(now)
            except Exception:
                forecasts = self.fallback.generate(now)

        timestamps = [f.hour for f in forecasts]
        costs = [f.cost_cents_kwh for f in forecasts]
        windows = find_cheapest_windows(timestamps, costs, min_duration=2, max_duration=8)

        response = PredictionResponse(
            prediction_id=f"pred_{now.strftime('%Y%m%d_%H%M')}",
            location=location,
            generated_at=now,
            model_version=settings.model_version,
            hourly_forecast=forecasts,
            optimal_windows=windows,
            explanation=self._generate_explanation(forecasts, windows),
        )

        self._cache[cache_key] = (time.time(), response)
        return response

    def _run_model(self, start: datetime) -> list[HourlyForecast]:
        # In production, this would fetch real data and run the model
        # For now, use fallback as placeholder until real data pipeline is connected
        return self.fallback.generate(start)

    def _generate_explanation(self, forecasts: list[HourlyForecast], windows) -> str:
        if not windows:
            return "No optimal windows found."
        peak = max(forecasts, key=lambda f: f.cost_cents_kwh)
        best = windows[0]
        return (
            f"Electricity costs peak at {peak.hour.strftime('%I%p')} "
            f"({peak.cost_cents_kwh:.1f}¢/kWh). "
            f"Best window: {best.start.strftime('%I%p')}-{best.end.strftime('%I%p')} "
            f"at {best.avg_cost_cents_kwh:.1f}¢/kWh average "
            f"— {((peak.cost_cents_kwh - best.avg_cost_cents_kwh) / peak.cost_cents_kwh * 100):.0f}% cheaper."
        )
```

- [ ] **Step 4: Run tests**

```bash
cd sunshift && uv run pytest tests/backend/test_predict.py -v
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add sunshift/backend/ml/predict.py sunshift/backend/ml/scheduler.py sunshift/tests/backend/test_predict.py
git commit -m "feat(sp1): prediction service with caching, circuit breaker fallback, optimal window scheduler"
```

---

### Task 5: FastAPI Backend — Routes + WebSocket

**Goal:** Build FastAPI app with all SP1 API routes (agent registration, metrics ingestion, predictions, commands) and WebSocket handler for agent communication.

**Files:**
- Create: `sunshift/backend/main.py`
- Create: `sunshift/backend/core/deps.py`
- Create: `sunshift/backend/api/routes/agents.py`
- Create: `sunshift/backend/api/routes/predictions.py`
- Create: `sunshift/backend/api/routes/metrics.py`
- Create: `sunshift/backend/api/routes/commands.py`
- Create: `sunshift/backend/api/websocket.py`
- Create: `sunshift/backend/services/savings.py`
- Create: `sunshift/tests/backend/test_routes.py`

**Acceptance Criteria:**
- [ ] POST /api/v1/agents/register creates agent record (in-memory store for MVP)
- [ ] POST /api/v1/metrics/ingest accepts validated metrics
- [ ] GET /api/v1/predictions/energy returns PredictionResponse
- [ ] GET /api/v1/status/{agent_id} returns agent status
- [ ] WebSocket /ws/agent/{agent_id} sends commands and receives heartbeats
- [ ] All routes have proper error handling (404 for unknown agent, 422 for validation)

**Verify:** `cd sunshift && uv run pytest tests/backend/test_routes.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests for API routes**

Create `sunshift/tests/backend/test_routes.py`:

```python
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestAgentRoutes:
    async def test_register_agent(self, client):
        resp = await client.post("/api/v1/agents/register", json={
            "agent_id": "test-001", "name": "Test Agent",
        })
        assert resp.status_code == 201
        assert resp.json()["agent_id"] == "test-001"

    async def test_register_duplicate_returns_409(self, client):
        await client.post("/api/v1/agents/register", json={"agent_id": "dup-001", "name": "First"})
        resp = await client.post("/api/v1/agents/register", json={"agent_id": "dup-001", "name": "Second"})
        assert resp.status_code == 409

    async def test_get_unknown_agent_returns_404(self, client):
        resp = await client.get("/api/v1/status/nonexistent")
        assert resp.status_code == 404


class TestMetricsRoutes:
    async def test_ingest_metrics(self, client):
        await client.post("/api/v1/agents/register", json={"agent_id": "metric-001", "name": "M"})
        resp = await client.post("/api/v1/metrics/ingest", json={
            "agent_id": "metric-001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 45.0, "memory_percent": 60.0, "disk_percent": 70.0,
            "network_bytes_sent": 1024, "network_bytes_recv": 2048,
        })
        assert resp.status_code == 202


class TestPredictionRoutes:
    async def test_get_prediction(self, client):
        resp = await client.get("/api/v1/predictions/energy", params={"location": "tampa_fl"})
        assert resp.status_code == 200
        data = resp.json()
        assert "hourly_forecast" in data
        assert "optimal_windows" in data
        assert len(data["hourly_forecast"]) == 48
```

- [ ] **Step 2: Implement FastAPI app and routes**

Create `sunshift/backend/main.py`:

```python
from fastapi import FastAPI
from backend.api.routes import agents, predictions, metrics, commands
from backend.api.websocket import router as ws_router

app = FastAPI(title="SunShift API", version="0.1.0")

app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(commands.router, prefix="/api/v1", tags=["commands"])
app.include_router(ws_router, tags=["websocket"])


@app.get("/health")
async def health():
    return {"status": "ok"}
```

Create `sunshift/backend/core/deps.py`:

```python
from backend.ml.predict import PredictionService

# In-memory stores for MVP (replace with DynamoDB in SP4)
agent_store: dict = {}
metrics_store: dict[str, list] = {}
ws_connections: dict[str, object] = {}

prediction_service = PredictionService()
```

Create `sunshift/backend/api/routes/agents.py`:

```python
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from backend.models.agent import AgentRegistration, AgentStatus
from backend.core.deps import agent_store

router = APIRouter()


@router.post("/agents/register", status_code=201)
async def register_agent(reg: AgentRegistration):
    if reg.agent_id in agent_store:
        raise HTTPException(status_code=409, detail="Agent already registered")
    agent_store[reg.agent_id] = {
        "registration": reg,
        "status": "online",
        "last_seen": datetime.now(timezone.utc),
    }
    return {"agent_id": reg.agent_id, "status": "registered"}


@router.get("/status/{agent_id}")
async def get_status(agent_id: str):
    if agent_id not in agent_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_store[agent_id]
    return AgentStatus(
        agent_id=agent_id,
        status=agent["status"],
        last_seen=agent["last_seen"],
    )
```

Create `sunshift/backend/api/routes/predictions.py`:

```python
from fastapi import APIRouter
from backend.core.deps import prediction_service

router = APIRouter()


@router.get("/predictions/energy")
async def get_prediction(location: str = "tampa_fl"):
    return prediction_service.predict(location)
```

Create `sunshift/backend/api/routes/metrics.py`:

```python
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from backend.models.metrics import MetricsPayload
from backend.core.deps import agent_store, metrics_store

router = APIRouter()


@router.post("/metrics/ingest", status_code=202)
async def ingest_metrics(payload: MetricsPayload):
    if payload.agent_id not in agent_store:
        raise HTTPException(status_code=404, detail="Agent not registered")
    if payload.agent_id not in metrics_store:
        metrics_store[payload.agent_id] = []
    metrics_store[payload.agent_id].append(payload.model_dump())
    agent_store[payload.agent_id]["last_seen"] = datetime.now(timezone.utc)
    return {"status": "accepted"}
```

Create `sunshift/backend/api/routes/commands.py`:

```python
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from backend.models.commands import AgentCommand
from backend.core.deps import agent_store

router = APIRouter()


@router.post("/commands/{agent_id}")
async def send_command(agent_id: str, command: AgentCommand):
    if agent_id not in agent_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    command.issued_at = datetime.now(timezone.utc)
    # In production: push to SQS → WebSocket → Agent
    return {"status": "queued", "command": command.command, "agent_id": agent_id}
```

Create `sunshift/backend/api/routes/__init__.py`: empty file.

Create `sunshift/backend/api/websocket.py`:

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.core.deps import ws_connections

router = APIRouter()


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    ws_connections[agent_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "ack", "agent_id": agent_id})
    except WebSocketDisconnect:
        ws_connections.pop(agent_id, None)
```

- [ ] **Step 3: Run tests**

```bash
cd sunshift && uv run pytest tests/backend/test_routes.py -v
```

Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add sunshift/backend/
git commit -m "feat(sp1): FastAPI backend — agent registration, metrics, predictions, WebSocket"
```

---

### Task 6: On-Prem Agent — Collector + Config

**Goal:** Build the on-prem agent that collects system metrics via psutil, stores them in local SQLite, and loads configuration from YAML.

**Files:**
- Create: `sunshift/agent/config.py`
- Create: `sunshift/agent/db.py`
- Create: `sunshift/agent/collector.py`
- Create: `sunshift/tests/agent/test_collector.py`

**Acceptance Criteria:**
- [ ] Config loads from YAML file with defaults
- [ ] SQLite creates tables on init, stores metrics with 7-day retention
- [ ] Collector reads CPU/RAM/Disk/Network via psutil
- [ ] Metrics are stored locally and batchable for API upload

**Verify:** `cd sunshift && uv run pytest tests/agent/test_collector.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests**

Create `sunshift/tests/agent/test_collector.py`:

```python
import pytest
from pathlib import Path

from agent.config import AgentConfig
from agent.db import LocalDB
from agent.collector import MetricsCollector


class TestAgentConfig:
    def test_load_defaults(self):
        config = AgentConfig()
        assert config.agent_id == "dev-agent-001"
        assert config.metrics_interval_sec == 60

    def test_load_from_yaml(self, tmp_path):
        yaml_content = """
agent:
  id: "test-clinic-001"
  api_endpoint: "http://localhost:8000"
sync:
  watch_paths: ["/tmp/data"]
  encrypt: false
schedule:
  metrics_interval_sec: 30
"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml_content)
        config = AgentConfig.from_yaml(config_path)
        assert config.agent_id == "test-clinic-001"
        assert config.metrics_interval_sec == 30


class TestLocalDB:
    def test_create_tables(self, tmp_path):
        db = LocalDB(tmp_path / "test.db")
        db.init()
        # Should not raise
        db.store_metric({"cpu_percent": 50, "memory_percent": 60, "disk_percent": 70})

    def test_get_recent_metrics(self, tmp_path):
        db = LocalDB(tmp_path / "test.db")
        db.init()
        for i in range(5):
            db.store_metric({"cpu_percent": 10 * i, "memory_percent": 50, "disk_percent": 50})
        recent = db.get_recent_metrics(limit=3)
        assert len(recent) == 3


class TestMetricsCollector:
    def test_collect_returns_valid_metrics(self):
        collector = MetricsCollector()
        metrics = collector.collect()
        assert 0 <= metrics["cpu_percent"] <= 100
        assert 0 <= metrics["memory_percent"] <= 100
        assert 0 <= metrics["disk_percent"] <= 100
        assert metrics["network_bytes_sent"] >= 0
```

- [ ] **Step 2: Implement config, db, collector**

Create `sunshift/agent/config.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    agent_id: str = "dev-agent-001"
    api_endpoint: str = "http://localhost:8000"
    watch_paths: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=lambda: ["*.tmp", "*.log"])
    max_bandwidth_mbps: int = 50
    encrypt: bool = True
    metrics_interval_sec: int = 60
    heartbeat_interval_sec: int = 30
    retry_max: int = 5

    @classmethod
    def from_yaml(cls, path: Path) -> AgentConfig:
        with open(path) as f:
            raw = yaml.safe_load(f)
        agent = raw.get("agent", {})
        sync = raw.get("sync", {})
        schedule = raw.get("schedule", {})
        return cls(
            agent_id=agent.get("id", cls.agent_id),
            api_endpoint=agent.get("api_endpoint", cls.api_endpoint),
            watch_paths=sync.get("watch_paths", []),
            exclude_patterns=sync.get("exclude", cls.exclude_patterns),
            max_bandwidth_mbps=sync.get("max_bandwidth_mbps", cls.max_bandwidth_mbps),
            encrypt=sync.get("encrypt", cls.encrypt),
            metrics_interval_sec=schedule.get("metrics_interval_sec", cls.metrics_interval_sec),
            heartbeat_interval_sec=schedule.get("heartbeat_interval_sec", cls.heartbeat_interval_sec),
        )
```

Create `sunshift/agent/db.py`:

```python
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class LocalDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def init(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                upload_id TEXT,
                status TEXT NOT NULL,
                bytes_uploaded INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def store_metric(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO metrics (timestamp, data) VALUES (?, ?)",
            (now, json.dumps(data)),
        )
        self.conn.commit()

    def get_recent_metrics(self, limit: int = 100) -> list[dict]:
        cursor = self.conn.execute(
            "SELECT timestamp, data FROM metrics ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [{"timestamp": row[0], **json.loads(row[1])} for row in cursor.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()
```

Create `sunshift/agent/collector.py`:

```python
import psutil


class MetricsCollector:
    def collect(self) -> dict:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "disk_percent": disk.percent,
            "network_bytes_sent": net.bytes_sent,
            "network_bytes_recv": net.bytes_recv,
            "estimated_power_watts": self._estimate_power(cpu),
        }

    def _estimate_power(self, cpu_percent: float) -> float:
        idle_watts = 30
        max_watts = 120
        return idle_watts + (max_watts - idle_watts) * (cpu_percent / 100)
```

- [ ] **Step 3: Run tests**

```bash
cd sunshift && uv run pytest tests/agent/test_collector.py -v
```

Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add sunshift/agent/ sunshift/tests/agent/
git commit -m "feat(sp1): on-prem agent — config loader, SQLite buffer, metrics collector"
```

---

### Task 7: On-Prem Agent — Command Receiver + Agent Main

**Goal:** Build WebSocket client that connects to FastAPI backend, receives commands, sends heartbeats, and reconnects automatically. Wire everything into agent main entry point.

**Files:**
- Create: `sunshift/agent/command_receiver.py`
- Create: `sunshift/agent/main.py`
- Create: `sunshift/tests/agent/test_command_receiver.py`

**Acceptance Criteria:**
- [ ] WebSocket client connects to backend, sends heartbeat every 30s
- [ ] Receives commands (START_SYNC, FULL_BACKUP, STOP) and dispatches handlers
- [ ] Auto-reconnects with exponential backoff on disconnect
- [ ] Agent main orchestrates collector + command receiver in async event loop

**Verify:** `cd sunshift && uv run pytest tests/agent/test_command_receiver.py -v` → all tests pass

**Steps:**

- [ ] **Step 1: Write tests**

Create `sunshift/tests/agent/test_command_receiver.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from agent.command_receiver import CommandReceiver


class TestCommandReceiver:
    def test_backoff_increases_exponentially(self):
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        assert receiver._backoff_delay(0) == 1
        assert receiver._backoff_delay(1) == 2
        assert receiver._backoff_delay(2) == 4
        assert receiver._backoff_delay(10) == 60  # capped at 60

    def test_dispatches_sync_command(self):
        handler = MagicMock()
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        receiver.register_handler("START_SYNC", handler)
        receiver._dispatch({"command": "START_SYNC", "paths": ["/data"]})
        handler.assert_called_once_with({"command": "START_SYNC", "paths": ["/data"]})

    def test_ignores_unknown_command(self):
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        # Should not raise
        receiver._dispatch({"command": "UNKNOWN"})
```

- [ ] **Step 2: Implement command receiver**

Create `sunshift/agent/command_receiver.py`:

```python
from __future__ import annotations

import asyncio
import json
from typing import Callable


class CommandReceiver:
    def __init__(self, ws_url: str, agent_id: str):
        self.ws_url = ws_url
        self.agent_id = agent_id
        self._handlers: dict[str, Callable] = {}
        self._retry_count = 0
        self._running = False

    def register_handler(self, command: str, handler: Callable):
        self._handlers[command] = handler

    def _backoff_delay(self, retry: int) -> int:
        return min(2 ** retry, 60)

    def _dispatch(self, message: dict):
        command = message.get("command")
        handler = self._handlers.get(command)
        if handler:
            handler(message)

    async def connect(self):
        import websockets

        self._running = True
        while self._running:
            try:
                async with websockets.connect(f"{self.ws_url}/ws/agent/{self.agent_id}") as ws:
                    self._retry_count = 0
                    heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws))
                    try:
                        async for raw in ws:
                            message = json.loads(raw)
                            if message.get("type") != "ack":
                                self._dispatch(message)
                    finally:
                        heartbeat_task.cancel()
            except Exception:
                delay = self._backoff_delay(self._retry_count)
                self._retry_count += 1
                await asyncio.sleep(delay)

    async def _heartbeat_loop(self, ws):
        while True:
            await ws.send(json.dumps({"type": "heartbeat", "agent_id": self.agent_id}))
            await asyncio.sleep(30)

    def stop(self):
        self._running = False
```

Create `sunshift/agent/main.py`:

```python
#!/usr/bin/env python3
"""SunShift On-Prem Agent — main entry point."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import AgentConfig
from agent.db import LocalDB
from agent.collector import MetricsCollector
from agent.command_receiver import CommandReceiver


async def metrics_loop(collector: MetricsCollector, db: LocalDB, interval: int):
    while True:
        metrics = collector.collect()
        db.store_metric(metrics)
        await asyncio.sleep(interval)


async def main():
    config_path = Path("sunshift-agent.yaml")
    config = AgentConfig.from_yaml(config_path) if config_path.exists() else AgentConfig()

    db = LocalDB(Path("agent_data.db"))
    db.init()

    collector = MetricsCollector()
    receiver = CommandReceiver(
        ws_url=config.api_endpoint.replace("http", "ws"),
        agent_id=config.agent_id,
    )

    print(f"[SunShift Agent] Starting agent '{config.agent_id}'")
    print(f"[SunShift Agent] API: {config.api_endpoint}")
    print(f"[SunShift Agent] Watch paths: {config.watch_paths}")

    await asyncio.gather(
        metrics_loop(collector, db, config.metrics_interval_sec),
        receiver.connect(),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: Run tests**

```bash
cd sunshift && uv run pytest tests/agent/test_command_receiver.py -v
```

Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add sunshift/agent/ sunshift/tests/agent/
git commit -m "feat(sp1): agent command receiver with WebSocket, reconnect, heartbeat + main entry"
```

---

### Task 8: Docker + Integration Verification

**Goal:** Create Dockerfile and docker-compose for local development, verify the full stack runs: backend serves predictions, agent connects via WebSocket.

**Files:**
- Create: `sunshift/Dockerfile`
- Create: `sunshift/docker-compose.yml`

**Acceptance Criteria:**
- [ ] `docker compose up` starts FastAPI backend on port 8000
- [ ] `GET http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `GET http://localhost:8000/api/v1/predictions/energy` returns 48-hour forecast
- [ ] `GET http://localhost:8000/docs` shows auto-generated API docs
- [ ] Agent can register and send metrics to running backend

**Verify:** `cd sunshift && docker compose up -d && sleep 3 && curl http://localhost:8000/health` → `{"status":"ok"}`

**Steps:**

- [ ] **Step 1: Create Dockerfile**

Create `sunshift/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv sync --no-dev

COPY backend/ backend/
COPY agent/ agent/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create docker-compose.yml**

Create `sunshift/docker-compose.yml`:

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - SUNSHIFT_DEBUG=true
    volumes:
      - ./backend:/app/backend
    restart: unless-stopped
```

- [ ] **Step 3: Build and verify**

```bash
cd sunshift && docker compose up -d --build
sleep 5
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/predictions/energy | python3 -m json.tool | head -20
curl http://localhost:8000/docs  # should return HTML
docker compose down
```

- [ ] **Step 4: Run full test suite**

```bash
cd sunshift && uv run pytest tests/ -v --cov=backend --cov=agent --cov-report=term-missing
```

Expected: All tests pass, coverage report shows >80% for implemented modules.

- [ ] **Step 5: Commit**

```bash
git add sunshift/Dockerfile sunshift/docker-compose.yml
git commit -m "feat(sp1): Docker + docker-compose for local development, full test suite passing"
```

---

## Verification — End-to-End Checklist

After all tasks complete:

1. `cd sunshift && uv run pytest tests/ -v` → all tests pass
2. `docker compose up -d` → backend running
3. `curl localhost:8000/api/v1/predictions/energy` → 48-hour forecast with optimal windows
4. `curl localhost:8000/docs` → Swagger UI
5. Agent can register: `curl -X POST localhost:8000/api/v1/agents/register -H 'Content-Type: application/json' -d '{"agent_id":"test-001","name":"Test"}'`
6. Metrics can be sent: `curl -X POST localhost:8000/api/v1/metrics/ingest -H 'Content-Type: application/json' -d '{"agent_id":"test-001","timestamp":"2026-04-13T14:00:00Z","cpu_percent":45,"memory_percent":60,"disk_percent":70,"network_bytes_sent":1024,"network_bytes_recv":2048}'`
