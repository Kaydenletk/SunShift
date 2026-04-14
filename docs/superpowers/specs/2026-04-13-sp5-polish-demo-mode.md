# SP5: Polish + Demo Mode — Design Specification

> **Goal:** Make SunShift interview-ready with a compelling demo experience and professional documentation.

## Overview

SP5 delivers three key artifacts that transform the technical implementation into a portfolio-ready product:

1. **Demo CLI Tool** — Interactive terminal experience showcasing all features
2. **README.md** — Professional product + technical documentation
3. **Technical Decisions Document** — ADR-based architecture rationale

## Success Criteria

- [ ] Demo runs with single command (`python -m sunshift.demo`)
- [ ] All 3 scenarios complete without errors
- [ ] README renders correctly on GitHub with badges
- [ ] Technical Decisions covers all 6 key architectural decisions
- [ ] No hardcoded paths or secrets in demo code

---

## 1. Demo CLI Tool

### Location
`sunshift/demo/` — New package within the sunshift directory

### Technology
- **Python `rich` library** for terminal UI (progress bars, panels, tables)
- **Mock data generators** for realistic simulation
- **Scenario orchestrator** for guided walkthroughs

### Scenarios

#### Scenario 1: Peak Hour Cost Optimization (2-3 min)
**Story:** It's 2 PM on a Tuesday. FPL TOU peak pricing kicks in.

**Flow:**
1. Show current workload status (3 VMs running locally)
2. Display real-time electricity pricing (peak: $0.18/kWh vs off-peak: $0.04/kWh)
3. Prophet model predicts next 4 hours of high pricing
4. System recommends migration to AWS Ohio
5. Animate migration progress with cost savings counter
6. Show final savings: "$47.20 saved today"

**Outputs:**
- Cost comparison table (local vs cloud)
- Migration timeline visualization
- Cumulative savings chart

#### Scenario 2: Hurricane Shield Alert (2-3 min)
**Story:** Category 3 hurricane "Elena" approaching Tampa Bay.

**Flow:**
1. NOAA API detects storm 200 miles from Tampa
2. Threat evaluator calculates 78% risk score
3. Gemini API generates executive alert
4. System triggers preemptive migration
5. Show workload evacuation to Ohio
6. Display recovery plan post-storm

**Outputs:**
- Storm tracking map (ASCII art)
- Alert message with severity indicators
- Migration checklist with status

#### Scenario 3: Weekly Analytics Report (1-2 min)
**Story:** End of week summary for business owner.

**Flow:**
1. Display 7-day cost history
2. Show prediction accuracy metrics
3. Highlight savings vs always-on-cloud
4. Present optimization recommendations

**Outputs:**
- Weekly cost breakdown table
- Prediction accuracy percentage
- Next week forecast

### CLI Interface

```bash
# Run all scenarios
python -m sunshift.demo

# Run specific scenario
python -m sunshift.demo --scenario peak
python -m sunshift.demo --scenario hurricane
python -m sunshift.demo --scenario analytics

# Quick mode (faster animations)
python -m sunshift.demo --quick

# Export results
python -m sunshift.demo --export results.json
```

### File Structure

```
sunshift/demo/
├── __init__.py
├── __main__.py           # Entry point
├── cli.py                # Argument parsing
├── scenarios/
│   ├── __init__.py
│   ├── base.py           # Base scenario class
│   ├── peak_hour.py      # Scenario 1
│   ├── hurricane.py      # Scenario 2
│   └── analytics.py      # Scenario 3
├── mock_data/
│   ├── __init__.py
│   ├── pricing.py        # FPL TOU mock data
│   ├── workloads.py      # VM/container mocks
│   ├── weather.py        # Hurricane mock data
│   └── predictions.py    # ML prediction mocks
├── ui/
│   ├── __init__.py
│   ├── panels.py         # Rich panels/boxes
│   ├── tables.py         # Data tables
│   ├── progress.py       # Progress bars
│   └── ascii_art.py      # Storm maps, logos
└── utils/
    ├── __init__.py
    ├── timing.py         # Animation timing
    └── export.py         # JSON export
```

### Sample Output

```
╭──────────────────────────────────────────────────────────────╮
│                    ☀️ SunShift Demo                          │
│              AI-Powered Compute Cost Optimizer               │
╰──────────────────────────────────────────────────────────────╯

Select scenario:
  [1] Peak Hour Cost Optimization
  [2] Hurricane Shield Alert
  [3] Weekly Analytics Report
  [A] Run All Scenarios

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Scenario 1: Peak Hour Cost Optimization
──────────────────────────────────────────

Current Time: 2:00 PM EDT (Peak Hours: 12 PM - 9 PM)

┌─────────────────┬──────────┬──────────┐
│ Workload        │ Location │ Status   │
├─────────────────┼──────────┼──────────┤
│ web-server-01   │ On-Prem  │ Running  │
│ api-server-01   │ On-Prem  │ Running  │
│ db-replica-01   │ On-Prem  │ Running  │
└─────────────────┴──────────┴──────────┘

⚡ Electricity Pricing:
  Current: $0.18/kWh (PEAK)
  Off-Peak: $0.04/kWh
  Multiplier: 4.5x

🔮 Prophet Prediction: Peak pricing continues until 9 PM

[████████████████████████████████████████] 100%
Migrating workloads to AWS Ohio...

💰 Savings Today: $47.20
```

---

## 2. README.md

### Location
`sunshift/README.md` — Root of sunshift directory

### Structure

```markdown
# ☀️ SunShift

> AI-Powered Compute Cost Optimizer for Florida SMBs

[Badges: Python 3.12 | Next.js 16 | AWS | License MIT]

## The Problem

Florida SMBs face two critical challenges:
1. **Electricity costs** — FPL TOU pricing charges 4.5x during peak hours
2. **Hurricane risk** — 60% of SMBs fail after natural disasters (FEMA)

## The Solution

SunShift automatically migrates workloads between on-premises and AWS based on:
- Real-time electricity pricing (Prophet + XGBoost prediction)
- Hurricane threat assessment (NOAA API + AI-generated alerts)

[Hero Screenshot/GIF of Demo]

## Quick Start

\`\`\`bash
# Clone and install
git clone https://github.com/username/sunshift
cd sunshift && uv sync

# Run the demo
python -m sunshift.demo

# Start development
cd dashboard && npm run dev  # Frontend
uv run uvicorn backend.main:app  # Backend
\`\`\`

## Architecture

[Mermaid diagram showing: On-Prem Agent ↔ Backend API ↔ AWS]

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| ML Engine | Prophet + XGBoost | Price prediction |
| Hurricane Shield | NOAA + Gemini/Claude | Threat assessment |
| Dashboard | Next.js 16 + Tailwind | Monitoring UI |
| Infrastructure | Terraform + ECS | Cloud deployment |

## Features

### 🔮 Predictive Cost Optimization
- 24-hour price forecasting with Prophet ensemble
- Optimal migration window scheduling
- Real-time savings tracking

### 🌀 Hurricane Shield
- NOAA NHC integration for storm tracking
- AI-generated executive alerts
- Preemptive workload evacuation

### 📊 Dashboard
- Real-time cost monitoring
- Prediction visualization
- Hurricane threat display

## Project Structure

\`\`\`
sunshift/
├── backend/        # FastAPI + ML Engine
├── dashboard/      # Next.js 16 Frontend
├── infra/          # Terraform IaC
├── demo/           # Interactive Demo
└── tests/          # 68+ tests
\`\`\`

## Technical Decisions

See [TECHNICAL_DECISIONS.md](./TECHNICAL_DECISIONS.md) for architecture rationale.

## Development

### Prerequisites
- Python 3.12+
- Node.js 22+
- uv (Python package manager)
- Terraform 1.9+ (for infrastructure)

### Running Tests

\`\`\`bash
cd sunshift && uv run pytest tests/ -v
\`\`\`

### Deploying Infrastructure

\`\`\`bash
cd sunshift/infra
./scripts/deploy.sh dev init
./scripts/deploy.sh dev apply
\`\`\`

## License

MIT License - See [LICENSE](./LICENSE)

---

Built with ❤️ for the 2026 portfolio season
```

### Key Elements

1. **Hero Section** — Clear value proposition with badges
2. **Problem/Solution** — Business context before technical details
3. **Quick Start** — 3-command setup for immediate engagement
4. **Architecture** — Visual diagram with component table
5. **Features** — Emoji-enhanced feature highlights
6. **Project Structure** — Clean directory overview
7. **Development** — Prerequisites and common commands

---

## 3. Technical Decisions Document

### Location
`sunshift/TECHNICAL_DECISIONS.md`

### Format
Hybrid: Executive Summary + ADR Collection

### Structure

```markdown
# Technical Decisions

## Executive Summary

SunShift is a hybrid cloud orchestration system designed for Florida SMBs
facing two challenges: volatile electricity pricing and hurricane risk.
This document explains the key architectural decisions and trade-offs.

The system uses a **Prophet + XGBoost ensemble** for price prediction,
achieving higher accuracy than either model alone. Infrastructure runs on
**AWS ECS Fargate** for zero-ops container management, with **Terraform**
enabling reproducible deployments. Hurricane alerts leverage **Gemini API**
with Claude fallback for reliability.

Key constraints: ~$15-20/month infrastructure budget, HIPAA-ready architecture
(for future healthcare segment), and Florida-specific regulatory compliance.

---

## ADR-001: Prophet + XGBoost Ensemble for Price Prediction

### Status
Accepted

### Context
Need to predict FPL TOU electricity prices 24 hours ahead to schedule
optimal migration windows. Predictions must account for:
- Daily seasonality (peak hours 12 PM - 9 PM)
- Weekly patterns (weekday vs weekend)
- Weather correlation (AC load during heat waves)

### Decision
Use Prophet for trend/seasonality decomposition combined with XGBoost
for residual correction.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Prophet only | Simple, interpretable | Misses non-linear patterns |
| XGBoost only | Handles complexity | Needs feature engineering |
| LSTM/Transformer | State-of-art | Overkill for this data volume |
| ARIMA | Classical, proven | Poor with multiple seasonality |

### Consequences
- Higher prediction accuracy (~15% improvement over Prophet alone)
- Two models to maintain
- Training pipeline complexity

---

## ADR-002: Single-Table DynamoDB Design

### Status
Accepted

### Context
Need to store workload states, migration history, and prediction cache
with low-latency access patterns.

### Decision
Use DynamoDB with single-table design pattern. Partition key design:
- `WL#<workload-id>` — Workload records
- `MIG#<date>#<id>` — Migration history
- `PRED#<date>#<hour>` — Prediction cache

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| PostgreSQL RDS | Relational queries | Higher cost, more ops |
| Aurora Serverless | Auto-scaling | Cold start latency |
| Redis | Ultra-fast | Data persistence concerns |

### Consequences
- Pay-per-request pricing fits budget
- Denormalized data requires careful access patterns
- No ad-hoc SQL queries

---

## ADR-003: Gemini API with Claude Fallback

### Status
Accepted

### Context
Hurricane alerts need AI-generated executive summaries. Must be reliable
during actual hurricane events when API availability may be impacted.

### Decision
Use Google Gemini as primary (lower cost, good quality) with Anthropic
Claude as fallback (higher quality, higher cost).

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| OpenAI GPT-4 | Widely used | Higher cost |
| Local LLM | No API dependency | Compute requirements |
| Template-based | Simple, reliable | Less dynamic |

### Consequences
- Dual API key management
- Automatic failover logic
- Cost optimization with quality fallback

---

## ADR-004: ECS Fargate over EC2

### Status
Accepted

### Context
Need to run backend containers with minimal operational overhead.

### Decision
Use AWS ECS Fargate for serverless container execution.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| ECS on EC2 | More control | Instance management |
| EKS | Industry standard | Complexity overkill |
| Lambda | True serverless | Cold starts, time limits |
| Bare EC2 | Full control | Full responsibility |

### Consequences
- Zero server management
- Per-second billing
- Slight cold start on scale-up

---

## ADR-005: EventBridge for Scheduling

### Status
Accepted

### Context
Need to trigger prediction updates and migration checks on schedule.

### Decision
Use AWS EventBridge Scheduler for cron-based invocations.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| CloudWatch Events | Same underlying service | Legacy naming |
| Step Functions | Visual workflows | Overkill for simple cron |
| In-app scheduler | Self-contained | Requires always-on instance |

### Consequences
- Native AWS integration
- Reliable invocation
- Slight latency for cold starts

---

## ADR-006: Terraform Modules over CDK

### Status
Accepted

### Context
Need reproducible infrastructure deployment with team familiarity.

### Decision
Use Terraform with modular structure (8 modules).

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| AWS CDK | TypeScript, type-safe | Learning curve |
| CloudFormation | Native AWS | Verbose YAML/JSON |
| Pulumi | Multi-language | Less ecosystem |
| Manual console | Quick prototyping | Not reproducible |

### Consequences
- Industry-standard IaC
- Module reusability
- State management required

---

## Trade-offs Considered But Rejected

### Multi-Region Deployment
**Why not:** Budget constraints (~$15-20/month target). Single region
(us-east-2) sufficient for demo/portfolio. Would add ~$30/month for
cross-region replication.

### Kubernetes (EKS)
**Why not:** Operational complexity unjustified for 2-3 services. ECS
Fargate provides container orchestration without cluster management.

### Real-time Streaming (Kinesis)
**Why not:** Batch predictions sufficient for hourly price updates.
Streaming would add cost without proportional value.

### GraphQL API
**Why not:** REST adequate for current use cases. GraphQL adds complexity
for simple CRUD + prediction endpoints.
```

---

## Implementation Phases

### Phase 1: Demo CLI Tool
1. Create `sunshift/demo/` package structure
2. Implement mock data generators
3. Build Scenario 1: Peak Hour
4. Build Scenario 2: Hurricane Shield
5. Build Scenario 3: Analytics
6. Add CLI argument parsing
7. Add export functionality

### Phase 2: README.md
1. Write hero section with badges
2. Add problem/solution narrative
3. Create architecture diagram
4. Document features with screenshots
5. Add development instructions

### Phase 3: Technical Decisions
1. Write executive summary
2. Create ADR-001 through ADR-006
3. Document rejected alternatives

### Phase 4: Final Polish
1. Test demo on fresh clone
2. Verify README renders correctly
3. Review all documentation
4. Create demo GIF/video

---

## Out of Scope

- Video recording (optional, user can do later)
- Deployment to production AWS
- CI/CD for demo package
- Unit tests for demo code (demo is itself the test)

---

## Dependencies

- SP1: Backend + ML Engine (for architecture reference)
- SP2: Dashboard (for screenshot in README)
- SP3: Hurricane Shield (for scenario 2 logic reference)
- SP4: Terraform (for ADR-006 content)
