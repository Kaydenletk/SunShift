# ☀️ SunShift

> AI-Powered Compute Cost Optimizer for Florida SMBs

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![AWS](https://img.shields.io/badge/AWS-ECS%20Fargate-orange.svg)](https://aws.amazon.com/ecs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## The Problem

Florida SMBs face two critical challenges:

1. **Electricity costs** — FPL TOU pricing charges 4.5x during peak hours (12 PM - 9 PM)
2. **Hurricane risk** — 60% of SMBs fail after natural disasters (FEMA)

## The Solution

SunShift automatically migrates workloads between on-premises and AWS based on:

- **Real-time electricity pricing** — Prophet + XGBoost ensemble predicts optimal migration windows
- **Hurricane threat assessment** — NOAA API integration with AI-generated executive alerts

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   On-Prem       │────▶│   SunShift      │────▶│   AWS Ohio      │
│   Workloads     │◀────│   Backend       │◀────│   (us-east-2)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │    Collector Agent    │    ML Predictions     │
        │    WebSocket Sync     │    Hurricane Shield   │
        └───────────────────────┴───────────────────────┘
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/khanhle/sunshift
cd sunshift && uv sync

# Run the interactive demo
python -m demo

# Or run a specific scenario
python -m demo --scenario peak      # Peak hour optimization
python -m demo --scenario hurricane # Hurricane shield
python -m demo --scenario analytics # Weekly report
```

## Architecture

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **ML Engine** | Prophet + XGBoost | 24-hour price prediction with 91.5% accuracy |
| **Hurricane Shield** | NOAA + Gemini/Claude | Real-time threat assessment + AI alerts |
| **Dashboard** | Next.js 16 + Tailwind | Monitoring UI with live metrics |
| **Infrastructure** | Terraform + ECS Fargate | Zero-ops cloud deployment |
| **On-Prem Agent** | Python + WebSocket | Local metrics collection + command execution |

## Features

### 🔮 Predictive Cost Optimization

- 24-hour price forecasting with Prophet + XGBoost ensemble
- Optimal migration window scheduling
- Real-time savings tracking with cumulative metrics

### 🌀 Hurricane Shield

- NOAA NHC integration for storm tracking
- Haversine distance-based threat evaluation
- AI-generated executive alerts (Gemini primary, Claude fallback)
- Preemptive workload evacuation

### 📊 Dashboard

- Real-time cost monitoring
- Prediction visualization with Recharts
- Hurricane threat display with risk scores
- Responsive design with light theme

## Project Structure

```
sunshift/
├── backend/           # FastAPI + ML Engine (51 tests)
│   ├── api/           # REST + WebSocket endpoints
│   ├── ml/            # Prophet + XGBoost prediction
│   └── services/      # Hurricane shield, scheduler
├── dashboard/         # Next.js 16 + Tailwind CSS v4
│   ├── app/           # App Router pages
│   └── components/    # Hero, charts, metrics
├── agent/             # On-prem collector agent
├── infra/             # Terraform IaC (8 modules)
│   ├── modules/       # networking, security, ecs, etc.
│   └── environments/  # dev configuration
├── demo/              # Interactive CLI demo
│   ├── scenarios/     # 3 demo scenarios
│   └── ui/            # Rich terminal UI
└── tests/             # 68+ tests total
```

## Development

### Prerequisites

- Python 3.12+
- Node.js 22+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Terraform 1.9+ (for infrastructure)

### Running Locally

```bash
# Backend
cd sunshift
uv run uvicorn backend.main:app --reload

# Dashboard
cd sunshift/dashboard
npm install && npm run dev

# Demo
cd sunshift
python -m demo --quick
```

### Running Tests

```bash
cd sunshift
uv run pytest tests/ -v --cov=backend --cov=agent

# Current: 68 tests passing, ~85% coverage
```

### Deploying Infrastructure

```bash
cd sunshift/infra

# Initialize (first time only)
./scripts/deploy.sh dev init

# Plan and apply
./scripts/deploy.sh dev plan
./scripts/deploy.sh dev apply
```

## Technical Decisions

See [TECHNICAL_DECISIONS.md](./TECHNICAL_DECISIONS.md) for architecture rationale, including:

- ADR-001: Prophet + XGBoost Ensemble
- ADR-002: Single-Table DynamoDB Design
- ADR-003: Gemini API with Claude Fallback
- ADR-004: ECS Fargate over EC2
- ADR-005: EventBridge for Scheduling
- ADR-006: Terraform Modules over CDK

## Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| ECS Fargate (2 tasks) | ~$8 |
| DynamoDB (on-demand) | ~$2 |
| S3 + CloudWatch | ~$3 |
| ALB | ~$5 |
| **Total** | **~$15-20** |

## License

MIT License — See [LICENSE](./LICENSE)

---

Built for the 2026 portfolio season | [View Technical Decisions](./TECHNICAL_DECISIONS.md)
