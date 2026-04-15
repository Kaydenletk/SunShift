# SunShift

**Hybrid cloud automation for Florida SMBs** — automatically migrate workloads based on electricity pricing and hurricane alerts.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## The Problem

Florida small businesses face two costly challenges:

1. **Peak electricity pricing** — FPL Time-of-Use rates are 4.5x higher during peak hours (12PM-9PM summer)
2. **Hurricane vulnerability** — 60% of SMBs fail after natural disasters (FEMA), yet most lack disaster recovery plans

## The Solution

SunShift is a hybrid cloud platform that:

- **Predicts optimal migration windows** using ML-based cost forecasting
- **Auto-migrates workloads** to AWS during peak pricing or hurricane threats
- **Maintains HIPAA compliance** for healthcare clients (BAA, AES-256 encryption, audit logs)
- **Provides real-time savings tracking** with ROI dashboards

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SunShift Platform                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   On-Premise    │    Backend      │         Dashboard           │
│     Agent       │    (FastAPI)    │         (Next.js)           │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Data collector│ • AI Scheduler  │ • Real-time status          │
│ • Command recv  │ • Window scoring│ • Savings tracker           │
│ • Health checks │ • Batching svc  │ • Hurricane alerts          │
│                 │ • Hurricane API │ • Workload management       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AWS Ohio      │
                    │   (us-east-2)   │
                    │                 │
                    │ • EC2 instances │
                    │ • S3 backups    │
                    │ • RDS replicas  │
                    └─────────────────┘
```

## Features

### AI Scheduler
- **Hybrid algorithm**: Greedy + Lookahead + Batching optimization
- **Window scoring**: Probabilistic formula (savings × confidence²)
- **Smart batching**: Queue similar workloads for efficient migration

### Hurricane Shield
- Real-time NHC data integration
- Automated evacuation triggers based on storm proximity
- Staged migration (critical → important → standard)

### Dashboard
- Live system status with health indicators
- Cumulative savings tracker
- Optimal migration window predictions
- Hurricane threat visualization

## Project Structure

```
sunshift/
├── agent/          # On-premise data collector & command receiver
├── backend/        # FastAPI backend
│   ├── api/        # REST endpoints
│   ├── services/   # Business logic (scheduler, hurricane, savings)
│   ├── models/     # Pydantic schemas
│   └── ml/         # ML models for prediction
├── dashboard/      # Next.js 15 frontend
├── demo/           # CLI demo with scenarios
├── tests/          # Test suite
└── scripts/        # Deployment & utilities
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)

### Backend

```bash
cd sunshift
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run API server
uvicorn backend.main:app --reload
```

### Dashboard

```bash
cd sunshift/dashboard
npm install
npm run dev
```

### Demo CLI

```bash
cd sunshift
python -m demo.cli --scenario peak_hour
python -m demo.cli --scenario hurricane
```

## Target Market

| Segment | Size | Key Requirements |
|---------|------|------------------|
| Healthcare | 5-50 employees | HIPAA compliance, 99.9% uptime |
| Law Firms | 5-30 employees | Data sovereignty, audit trails |
| Accounting | 5-20 employees | Seasonal scaling, data security |

## Key Metrics

- **Peak savings**: Up to 70% reduction in compute costs during TOU peak hours
- **RTO**: < 15 minutes for critical workload recovery
- **Compliance**: HIPAA, SOC 2 Type II ready

## Documentation

- [Research Synthesis](RESEARCH_SYNTHESIS.md) — Market research, competitive analysis
- [UX Research](ux-research/UX_RESEARCH_DELIVERABLE.md) — Personas, journey maps

## Roadmap

- [x] Market research & UX design
- [x] AI Scheduler service
- [x] Dashboard MVP
- [ ] Agent deployment package
- [ ] AWS integration
- [ ] HIPAA certification

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built for Florida SMBs who refuse to let hurricanes or peak pricing shut them down.
