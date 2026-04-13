# SunShift MVP — Design Specification

**Product:** SunShift — AI-Powered Compute Cost Optimizer
**Date:** 2026-04-13
**Status:** Approved
**Purpose:** Portfolio project for AI Engineer + Cloud Architect roles

---

## 1. Product Vision

SunShift uses ML to predict electricity costs and automatically schedules compute workloads to minimize energy expenses.

**Core ML model:** Predict electricity cost per hour from weather + historical grid data + seasonal patterns → find optimal windows for workload execution.

**Two use cases:**
- **Use Case 1 (primary):** SMB server backup/sync — shift to off-peak hours + hurricane auto-backup
- **Use Case 2 (stretch):** AI training job scheduling — schedule GPU training during cheapest hours

**Interview story:**
> "I built a system that uses ML to predict energy costs and automatically schedules compute workloads — whether that's a dental office backing up patient records or an ML team scheduling training jobs — to minimize electricity costs. Architecture: event-driven on AWS with Lambda, EventBridge, S3, Terraform IaC."

---

## 2. System Architecture

### 2.1 Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│  ON-PREM (MacBook local / Customer office)  │
│  ┌─────────────────────────────────────┐    │
│  │ Python Agent                        │    │
│  │ • Collector (metrics every 60s)     │    │
│  │ • Sync Engine (S3 multipart upload) │    │
│  │ • Command Receiver (WebSocket)      │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼───────────────────────────┘
                  │ HTTPS / encrypted
                  ▼
┌─────────────────────────────────────────────┐
│  AWS CLOUD (us-east-2 Ohio)                 │
│                                             │
│  EventBridge (event bus)                    │
│  ├── NOAA alerts                            │
│  ├── TOU schedule triggers                  │
│  ├── Agent heartbeats                       │
│  └── ML prediction events                   │
│                                             │
│  ┌──────┐ ┌───────┐ ┌──────────┐ ┌───────┐ │
│  │ML    │ │FastAPI│ │Hurricane │ │Orches-│ │
│  │Engine│ │(ECS)  │ │Shield    │ │trator │ │
│  │      │ │       │ │(Lambda)  │ │(SQS)  │ │
│  └──────┘ └───────┘ └──────────┘ └───────┘ │
│                                             │
│  ┌─────┐ ┌────────┐ ┌──────────┐           │
│  │ S3  │ │DynamoDB│ │CloudWatch│           │
│  └─────┘ └────────┘ └──────────┘           │
└─────────────────────────────────────────────┘
                  │ API calls
                  ▼
┌─────────────────────────────────────────────┐
│  FRONTEND (Vercel)                          │
│  Next.js Dashboard + shadcn/ui              │
│  Status | Predictions | Savings | Alerts    │
└─────────────────────────────────────────────┘
```

### 2.2 Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Event-driven | EventBridge central bus | Loose coupling, scalable, showcase for interview |
| Serverless-first | Lambda + Fargate | No server management, low cost at demo scale |
| DynamoDB over RDS | Single-table design | Time-series friendly, serverless pricing, no cold start |
| Encryption everywhere | KMS + TLS 1.3 | HIPAA-ready, security-conscious architecture |
| S3 multipart upload | Resumable uploads | Handles unreliable network (hurricane scenario) |

### 2.3 Data Flows

**Daily Energy Optimization:**
1. ML Engine fetches weather + grid data hourly
2. Predicts electricity demand → optimal migration window
3. EventBridge triggers Orchestrator at predicted peak
4. Orchestrator evaluates agent status → pushes command via SQS
5. FastAPI relays via WebSocket → Agent encrypts + uploads to S3
6. Dashboard updates: "$X saved today"

**Hurricane Shield:**
1. EventBridge polls NOAA API every 30 minutes
2. Detects storm advisory → triggers Hurricane Shield Lambda
3. Lambda evaluates threat level → sends FULL_BACKUP command
4. Agent encrypts + uploads all data to S3
5. Push notification: "Data safe ✓"

---

## 3. Tech Stack

| Layer | Technology | Portfolio Justification |
|-------|-----------|----------------------|
| Backend/AI | Python + FastAPI | AI/ML lingua franca, async, type-safe |
| ML Models | XGBoost + Prophet | Ensemble: time-series baseline + multi-factor prediction |
| LLM | Claude API | NLP analysis of NOAA bulletins + natural language alerts |
| Frontend | Next.js 15 + Tailwind + shadcn/ui | React framework #1, App Router, Server Components |
| IaC | Terraform | Cloud-agnostic, asked in 90% Cloud Architect interviews |
| AWS Services | S3, Lambda, EventBridge, SQS, KMS, DynamoDB, ECS Fargate, CloudWatch | Event-driven microservices showcase |
| Containers | Docker + ECS Fargate | Serverless containers |
| CI/CD | GitHub Actions | Lint → Test → Terraform plan → Deploy |
| Auth | Clerk | Free tier (10K MAU), Next.js native |
| Dashboard Deploy | Vercel | Free, zero-config |
| Experiment Tracking | MLflow | Model versioning, comparison, drift detection |

---

## 4. ML Engine — The Hero Component

### 4.1 Data Sources (all FREE APIs)

| Source | API | Features Extracted |
|--------|-----|-------------------|
| Weather | OpenWeatherMap (free: 1000 calls/day) | temperature, humidity, cloud_cover, wind_speed, forecast_48h |
| Grid/Electricity | EIA Open Data (free) | hourly_demand_mwh, day_ahead_price, generation_mix |
| Grid (supplemental) | GridStatus.io (free) | ISO-level real-time data |
| Time/Calendar | Self-generated | hour_sin/cos, day_of_week, month, is_holiday, is_fpl_peak |
| Hurricane | NOAA NHC (free, GeoJSON) | active_storms, distance_to_tampa_km, storm_category, eta_hours |

### 4.2 Feature Engineering

| Feature | Type | Rationale |
|---------|------|-----------|
| `temp_rolling_6h` | Rolling mean | AC load follows temperature trend, not instant value |
| `demand_lag_24h` | Lag | Today's demand similar to yesterday same hour |
| `demand_lag_168h` | Lag | Weekly pattern (same day last week) |
| `hour_sin` / `hour_cos` | Cyclical encoding | Hour 23 is near hour 0, not far from it |
| `temp_x_hour` | Interaction | 95°F at 2PM ≠ 95°F at 2AM (different AC demand) |
| `is_peak_transition` | Binary | 30 min before/after peak = decision moment |
| `cooling_degree_hours` | Derived | max(0, temp - 65°F) × hours — AC demand proxy |

### 4.3 Model Architecture — Ensemble

**Prophet** (baseline):
- Captures daily/weekly/yearly seasonality
- Handles holidays automatically
- Output: hourly demand baseline for 48h

**XGBoost** (primary predictor):
- Combines ALL features (weather, time, grid, Prophet baseline)
- Feature importance for explainability
- Fast inference (<50ms), production-ready
- Output: hourly cost prediction + confidence score

**Claude API** (intelligence layer):
- Analyzes NOAA bulletin text (NLP)
- Generates natural language alerts for non-tech users
- Explains predictions: "Costs peak at 4PM due to 94°F forecast..."
- Anomaly reasoning

### 4.4 Ensemble Logic (pseudo-code)

```python
def predict_optimal_schedule(target_date, location):
    # 1. Prophet: seasonal baseline
    baseline = prophet_model.predict(target_date, periods=48)

    # 2. XGBoost: multi-factor adjustment
    features = build_features(weather, grid_data, calendar, baseline)
    hourly_cost = xgboost_model.predict(features)
    confidence = xgboost_model.predict_confidence(features)

    # 3. Find optimal windows (cheapest consecutive hours)
    windows = find_cheapest_windows(
        hourly_cost, min_duration=2, max_duration=8,
        workload_type="backup"  # or "ai_training"
    )

    # 4. Claude: generate human explanation
    explanation = claude.explain(
        prediction=hourly_cost, optimal_window=windows[0],
        factors={"temperature": 94, "demand_forecast": "high"}
    )

    return {
        "hourly_forecast": hourly_cost,
        "optimal_windows": windows,
        "estimated_savings": calculate_savings(windows[0]),
        "confidence": confidence,
        "explanation": explanation
    }
```

### 4.5 Training Pipeline

**Initial (bootstrap):** Collect 1-2 years historical data from EIA API + weather history. Train offline (Jupyter). Upload model artifacts to S3.

**Production (continuous):**
- Lambda cron: collect new data daily
- Weekly: retrain XGBoost on rolling 90-day window
- Monthly: retrain Prophet with updated seasonality
- A/B compare: new vs. production model
- Auto-promote if MAPE improves
- Alert if model drift detected (MAPE > 15%)
- Shadow mode: new model runs 7 days in parallel before promotion

### 4.6 Production ML Patterns

| Pattern | Implementation |
|---------|---------------|
| **Fallback (Circuit Breaker)** | If ML fails or confidence < 0.5 → fallback to static TOU schedule (12PM-9PM = peak) |
| **Feature Store** | DynamoDB table caching computed features — avoids recomputation |
| **Experiment Tracking** | MLflow — track hyperparameters, metrics, model artifacts per training run |
| **Prediction Caching** | Cache predictions for 1 hour at API layer — <5ms for cached responses |
| **Shadow Mode** | New model runs parallel with production for 7 days before promotion |
| **Data Quality** | Pydantic validation on every API response. Null → fallback to last known value. Stale data → flag "low confidence" |

### 4.7 Evaluation Metrics

| Metric | Target |
|--------|--------|
| MAPE (cost prediction) | <10% |
| MAE (demand prediction) | <200 MW |
| Peak detection accuracy | >85% |
| Optimal window accuracy | >80% |
| Prediction latency (p95) | <500ms |
| Avg daily savings (SMB) | $3-5/day |
| Avg daily savings (AI training) | $15-40/day |

---

## 5. On-Prem Agent

### 5.1 Three Modules

**Collector:** CPU/RAM/Disk/Network metrics via psutil. Every 60s → local SQLite buffer (7-day retention).

**Sync Engine:** File watcher (watchdog). Incremental delta sync. AES-256-GCM encrypt before upload. S3 multipart upload (resumable). Bandwidth throttling configurable.

**Command Receiver:** WebSocket to FastAPI. Commands: START_SYNC, FULL_BACKUP, STOP. Heartbeat every 30s. Auto-reconnect with exponential backoff. Offline command queue when network lost.

### 5.2 Config

```yaml
agent:
  id: "clinic-dr-nguyen-001"
  api_endpoint: "https://api.sunshift.io"
sync:
  watch_paths: [/data/patient-records, /data/case-files]
  exclude: ["*.tmp", "*.log", "thumbs.db"]
  max_bandwidth_mbps: 50
  encrypt: true
schedule:
  metrics_interval_sec: 60
  heartbeat_interval_sec: 30
resilience:
  retry_max: 5
  retry_backoff: exponential
  offline_queue_max_mb: 100
```

### 5.3 Resilience Patterns

| Pattern | Implementation |
|---------|---------------|
| Upload resilience | S3 multipart + local upload journal + exponential backoff (1s→2s→4s→8s→max 60s) |
| Event resilience | SQS Dead Letter Queue + EventBridge 3 retries + idempotent handlers |
| Agent resilience | Offline command queue + WebSocket auto-reconnect + systemd auto-restart |

---

## 6. FastAPI Backend

### 6.1 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/agents/register` | Agent registration |
| POST | `/api/v1/metrics/ingest` | Receive metrics from agent |
| GET | `/api/v1/predictions/energy` | ML predictions (48h forecast) |
| GET | `/api/v1/status/{agent_id}` | Agent status |
| GET | `/api/v1/savings/summary` | Savings dashboard data |
| POST | `/api/v1/commands/{agent_id}` | Send command to agent |
| WS | `/ws/agent/{agent_id}` | WebSocket real-time channel |
| GET | `/api/v1/hurricane/status` | Hurricane alert status |

### 6.2 Project Structure

```
sunshift/
├── agent/                  # On-prem agent (standalone)
│   ├── collector.py
│   ├── sync_engine.py
│   ├── command_receiver.py
│   └── config.py
├── backend/                # FastAPI backend
│   ├── api/routes/         # agents, metrics, predictions, commands, hurricane
│   ├── api/websocket.py
│   ├── services/           # orchestrator, hurricane_shield, savings_calculator
│   ├── ml/                 # model, features, data_pipeline, predict
│   ├── models/             # Pydantic schemas
│   ├── core/               # Config, security, deps
│   └── main.py
├── dashboard/              # Next.js (SP2)
├── infra/                  # Terraform (SP4)
│   ├── modules/
│   └── environments/
├── tests/
├── docker-compose.yml
└── Dockerfile
```

---

## 7. Data Model

### 7.1 Storage Architecture

| Store | Purpose | Encryption |
|-------|---------|-----------|
| **S3** `sunshift-customer-data/` | Customer backups | AES-256 SSE-KMS |
| **S3** `sunshift-ml-artifacts/` | Model files, training data | Default SSE |
| **S3** `sunshift-raw-data/` | Weather, grid, NOAA raw responses | Default SSE |
| **S3** `sunshift-audit-logs/` | HIPAA audit trail | SSE-KMS + Object Lock |
| **DynamoDB** | Agents, predictions, features, savings, migrations | AWS-owned CMK |
| **SQLite** (agent) | Local metrics buffer, sync journal, command queue | — |

### 7.2 DynamoDB Single-Table Design

| Entity | PK | SK | Access Pattern |
|--------|----|----|----------------|
| Agent | `AGENT#<id>` | `PROFILE` | Get agent config + status |
| Agent Metrics | `AGENT#<id>` | `METRIC#<timestamp>` | Time-range query |
| Prediction | `PRED#<location>#<date>` | `HOUR#<HH>` | All hourly predictions for a day |
| Feature Cache | `FEAT#<location>#<date>` | `SET#<feature_set>` | Pre-computed features |
| Savings | `AGENT#<id>` | `SAVE#<date>` | Savings history for dashboard |
| Migration Log | `AGENT#<id>` | `MIG#<timestamp>` | Migration audit trail |

**GSI-1:** `GSI1PK = location | GSI1SK = timestamp` — Query by location
**TTL:** metrics (30 days), predictions (7 days), features (24 hours)

### 7.3 S3 Lifecycle Policies

| Bucket | Rule |
|--------|------|
| `raw-data/` | S3 Intelligent-Tiering (auto cost optimization) |
| `customer-data/` | Standard 90 days → Glacier after 1 year |
| `audit-logs/` | Glacier Deep Archive after 7 years |

---

## 8. Security

### 8.1 Encryption

| Layer | Method |
|-------|--------|
| At rest (S3) | AES-256 via SSE-KMS (per-customer CMK) |
| At rest (DynamoDB) | AWS-owned CMK |
| In transit | TLS 1.3 (agent ↔ API, API ↔ AWS) |
| Agent → S3 | Client-side AES-256-GCM BEFORE upload |
| Key management | AWS KMS |

### 8.2 Authentication

| Channel | Method |
|---------|--------|
| Dashboard users | JWT via Clerk |
| Agent → API | API Key + mTLS |
| API → AWS | IAM roles (least privilege) |
| Multi-tenant | Agent_id scoped access |

### 8.3 HIPAA Readiness

- AES-256 encryption at rest + in transit
- Per-customer KMS keys
- Immutable audit logs (S3 Object Lock)
- IAM least-privilege roles
- Multi-tenant data isolation
- BAA with AWS (sign when needed)

---

## 9. Sub-project Roadmap

### Vertical Slice Strategy — Build Order

| # | Sub-project | Scope | Timeline | Demo-able? |
|---|-------------|-------|----------|------------|
| 1 | **Core Pipeline + ML Engine** | Agent + FastAPI + ML prediction + S3 sync | 2-3 weeks | API only |
| 2 | **Dashboard MVP** | Next.js + charts + real-time status + Vercel | 1-2 weeks | **Live URL** |
| 3 | **Hurricane Shield** | NOAA + EventBridge + auto-backup + Claude NLP | 1 week | Simulate mode |
| 4 | **Terraform + Production** | IaC modules + CI/CD + monitoring + environments | 1-2 weeks | Infra code |
| 5 | **Polish + Demo Mode** | 1-click simulation + README + Technical Decisions doc | 1 week | **Full demo** |

**Total:** ~6-9 weeks
**Interview-ready:** After SP3 (must-haves complete)
**Impressive:** After SP5 (full polish)

### Exit Criteria — "Interview Ready"

**Must Have (SP1-SP3):**
- ML model predicting energy costs with MAPE <10%
- Live dashboard at a URL with real predictions
- Hurricane Shield demo-able (simulate mode)
- Agent running on MacBook, syncing to S3
- Production README + Technical Decisions document

**Nice to Have (SP4-SP5):**
- Terraform modules for all AWS resources
- CI/CD pipeline via GitHub Actions
- Demo Mode (1-click full simulation)
- AI training job scheduling use case
- 2-minute video demo

---

## 10. AWS Cost Estimate (Demo Scale)

| Service | Usage | Est. Cost/mo |
|---------|-------|-------------|
| S3 (10GB) | Demo data + ML artifacts | $0.23 |
| DynamoDB (on-demand) | ~100K reads + 50K writes | ~$1-2 |
| Lambda | ~500K invocations (free tier) | $0 |
| ECS Fargate (FastAPI) | 0.25 vCPU, 0.5GB, 24/7 | ~$9 |
| EventBridge | ~50K events/mo | $0.05 |
| CloudWatch | Logs + metrics | ~$3 |
| KMS | 1 CMK + API calls | $1 |
| Vercel (Dashboard) | Hobby plan | $0 |
| **TOTAL** | | **~$15-20/month** |

---

## 11. Research Foundation

This design is based on:
- `RESEARCH_SYNTHESIS.md` — Market research, competitive analysis, electricity pricing data
- `ux-research/UX_RESEARCH_DELIVERABLE.md` — 3 personas, journey maps, usability testing framework
- Web research on AI infrastructure cost optimization market (2026)
- Portfolio best practices research for AI Engineer + Cloud Architect roles (2026)
