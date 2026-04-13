# SunShift — Hybrid Cloud System for Florida SMBs

## Project Overview
- Hybrid cloud platform that auto-migrates workloads based on electricity TOU pricing + hurricane alerts
- Target market: Small businesses (5-50 employees) in Tampa Bay, Florida
- Key segments: Healthcare (HIPAA), Law firms, Accounting firms
- AWS Ohio (us-east-2) as cloud destination

## Communication
- User communicates in Vietnamese — respond in Vietnamese
- Technical terms can remain in English

## Project Phase
- Research + UX Design phase (no production code yet)
- Key documents:
  - `RESEARCH_SYNTHESIS.md` — Market research, competitive analysis, pricing data
  - `ux-research/UX_RESEARCH_DELIVERABLE.md` — Personas, journey maps, usability testing framework
  - `ux-research/sunshift_persona_data.py` — Persona generation script

## Tech Decisions (Pending)
- Tech stack not yet chosen — ask user before assuming
- Architecture not yet designed — reference research for requirements

## Key Domain Context
- FPL TOU peak hours: 12PM-9PM summer (4.5x off-peak price)
- HIPAA compliance is mandatory for healthcare segment (BAA, AES-256, audit logs)
- Hurricane season: June-November — core value proposition window
- 60% of SMBs fail after natural disasters (FEMA) — emotional selling point
