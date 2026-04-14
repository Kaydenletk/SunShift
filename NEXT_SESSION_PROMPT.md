# SunShift — Next Session Prompt

Copy-paste this to start the next Claude Code session:

---

## Prompt

Tiếp tục với SunShift — AI-Powered Compute Cost Optimizer. Đây là portfolio project cho AI Engineer + Cloud Architect roles.

### Trạng thái hiện tại

**Đã hoàn thành (5/5 sub-projects):** PROJECT COMPLETE

- **SP1: Core Pipeline + ML Engine** (51 tests) — FastAPI backend, Prophet + XGBoost ensemble, on-prem agent (collector, WebSocket command receiver, SQLite buffer), prediction service with caching + circuit breaker, optimal window scheduler
- **SP2: Dashboard MVP** (Next.js 16) — Brand redesign "Your Data Weather Station", hero status banner (3 states: protected/peak/hurricane), prediction chart (Recharts), savings tracker, hurricane card, quick stats, responsive, light theme, Vercel-ready
- **SP3: Hurricane Shield** (68 tests total) — NOAA NHC API client, haversine distance threat evaluator, shield orchestrator with demo mode, Gemini + Claude API alert generation, FastAPI hurricane routes
- **SP4: Terraform Infrastructure** — 8 modules (networking, security, storage, database, ecs, events, monitoring), GitHub Actions CI/CD, deploy script, us-east-2 (Ohio), ~$15-20/month
- **SP5: Polish + Demo Mode** — Interactive demo CLI, professional README, Technical Decisions doc (6 ADRs), MIT license

### SP5 Completed

- **Demo CLI** (`python -m sunshift.demo`)
  - 3 scenarios: Peak Hour, Hurricane Shield, Weekly Analytics
  - Rich terminal UI (tables, progress bars, ASCII art)
  - Options: `--scenario`, `--quick`, `--all`, `--export`
- **README.md** — Badges, problem/solution, architecture diagram, quick start, features
- **TECHNICAL_DECISIONS.md** — Executive summary + 6 ADRs (Prophet+XGBoost, DynamoDB, Gemini/Claude, ECS Fargate, EventBridge, Terraform)
- **LICENSE** — MIT

### Key files
- Demo: `sunshift/demo/` (CLI + 3 scenarios)
- Docs: `sunshift/README.md`, `sunshift/TECHNICAL_DECISIONS.md`
- Backend: `sunshift/backend/` (FastAPI + ML)
- Dashboard: `sunshift/dashboard/` (Next.js 16)
- Terraform: `sunshift/infra/` (8 modules + dev environment)

### Tech stack
- Backend: Python 3.12, FastAPI, XGBoost, Prophet, boto3
- Frontend: Next.js 16, Tailwind CSS v4, shadcn/ui, Recharts
- Demo: Python rich + typer
- AI: Gemini API (primary), Claude API (fallback) for hurricane alerts
- IaC: Terraform 1.9+, AWS provider ~> 5.0
- Deploy: Vercel (dashboard), AWS ECS Fargate (backend), us-east-2 (Ohio)

### Quick Commands
```bash
# Run demo
cd sunshift && python -m demo --quick

# Dashboard dev server
cd sunshift/dashboard && npm run dev

# Backend
cd sunshift && uv run uvicorn backend.main:app

# Tests
cd sunshift && uv run pytest tests/ -v

# Terraform deploy
cd sunshift/infra && ./scripts/deploy.sh dev apply
```

### Notes
- `.env` has Gemini API key (not committed)
- Giao tiếp bằng tiếng Việt, technical terms tiếng Anh OK
- Project is **interview-ready**

### Việc có thể làm tiếp (optional)
1. **Deploy dashboard** lên Vercel để có live URL
2. **Deploy backend** lên AWS với Terraform
3. **Record demo video** cho portfolio
4. **Fix failing tests** (24 backend tests need attention)
