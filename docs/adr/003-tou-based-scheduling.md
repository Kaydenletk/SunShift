# ADR-003: TOU-Based Workload Scheduling

**Status:** Accepted
**Date:** 2026-04-01
**Deciders:** SunShift Architecture Team

---

## Context

Florida Power & Light (FPL) operates a Time-of-Use (TOU) commercial rate structure that
creates extreme price differentials between peak and off-peak electricity windows.
For SMBs running compute workloads (backup jobs, ETL pipelines, report generation,
batch processing), the timing of execution directly determines the electricity bill.

### FPL Commercial TOU Rate Table

| Period | Summer (Apr–Oct) | Winter (Nov–Mar) |
|---|---|---|
| Off-peak (all other hours) | 6.0¢/kWh | 5.5¢/kWh |
| On-peak (12PM–9PM weekdays) | 27.0¢/kWh | 14.0¢/kWh |
| Peak multiplier | **4.5x** | **2.5x** |
| Demand charge (kW) | $9.36/kW | $9.36/kW |

Source: FPL Business TOU-1 rate schedule, effective January 2025.

A server drawing 2kW running a 4-hour backup during summer peak:
- Peak cost: 2 kW × 4 hr × $0.27/kWh = **$2.16**
- Off-peak cost: 2 kW × 4 hr × $0.06/kWh = **$0.48**
- **Savings per job: $1.68 (78% reduction)**

For a business running 3–5 such jobs per day, shifting to off-peak yields
**$100–150/month in electricity savings** — a figure that exceeds SunShift's own
subscription cost at the Growth tier ($99/mo).

Three scheduling approaches were evaluated:

| Approach | Complexity | Accuracy | Resilience |
|---|---|---|---|
| Static TOU schedule | Low | Medium (misses demand charge optimization) | High (no external dependencies) |
| Real-time grid price feed | High (third-party API dependency) | High | Low (API outage = no scheduling) |
| **ML-powered + static fallback (chosen)** | Medium | High | High (fallback ensures jobs always run) |

---

## Decision

We adopt an **ML-powered scheduler with a static TOU fallback circuit breaker**.

### ML Component

The primary scheduler uses two models in ensemble:

- **XGBoost** — classifies each upcoming 30-minute window as "schedule" or "defer"
  based on historical FPL demand patterns, Tampa Bay weather data, and calendar
  features (day-of-week, holidays, season).
- **Prophet** — provides time-series cost forecasts for the next 24-hour window,
  enabling the scheduler to rank future windows and batch multiple jobs optimally.

Model inputs:
- Current TOU period (derived from FPL schedule)
- Ambient temperature (Tampa Bay NWS feed)
- Historical demand patterns (30-day rolling window)
- Day type (weekday / weekend / FPL holiday)
- Season (summer = Apr-Oct, winter = Nov-Mar)

Model output: confidence score (0.0–1.0) per 30-minute window, with recommended
action (SCHEDULE_NOW / DEFER / BATCH_LATER).

### Hybrid Algorithm

```
For each pending job:
  1. Greedy pass: is current window off-peak AND confidence >= 70%? → SCHEDULE_NOW
  2. Lookahead pass: scan next 4-hour window for lower-cost slot → BATCH_LATER
  3. Deadline check: has job waited > 8 hours? → SCHEDULE_NOW (deadline flush)
  4. Emergency: hurricane alert active? → BYPASS_SCHEDULING (immediate execution)
```

### Static Fallback

If ML model confidence < 70% OR if the ML service is unavailable, the scheduler falls
back to deterministic TOU rules:
- Summer: schedule outside 12PM–9PM window
- Winter: schedule outside 12PM–9PM window (reduced urgency, 2.5x multiplier)
- Weekend: any window acceptable (TOU peak does not apply on weekends under FPL TOU-1)

The fallback is always valid — it captures the 4.5x rate arbitrage even without
ML optimization, at the cost of not capturing demand-charge micro-optimizations.

### Architecture

```
EventBridge (30-min cron)
  → Lambda: fetch TOU window + weather data
  → ML inference (SageMaker endpoint or local model cache)
  → If confidence >= 0.70: schedule job
  → If confidence < 0.70: apply static TOU fallback
  → SQS job queue → Lambda worker → on-prem agent
```

---

## Consequences

### Positive

- **$100–150/mo savings** for a typical SMB running 3–5 batch jobs per day during
  summer peak hours — the savings directly offset or exceed the SunShift subscription
- **ML optimization captures demand-charge arbitrage** that static rules miss; over a
  full summer billing cycle, this adds 15–20% additional savings vs. static-only
- **Circuit breaker ensures jobs always complete:** No job is stuck indefinitely waiting
  for an optimal window — the deadline flush runs after 8 hours regardless of ML state
- **Weekend scheduling is effectively free:** FPL TOU-1 peak pricing does not apply on
  weekends; weekend jobs always run at off-peak rates

### Negative

- **ML pipeline maintenance:** XGBoost and Prophet models require periodic retraining
  as FPL rate structures change. Rate updates have historically occurred 1–2 times per
  year. Model refresh cadence: quarterly.
- **SageMaker inference cost:** Running an inference endpoint 24/7 adds ~$30–50/mo
  (ml.t3.medium). Mitigation: use Lambda-based inference with model bundled in Lambda
  layer (eliminates always-on endpoint cost).
- **Model cold-start:** If Lambda inference layer is evicted, first invocation adds
  ~800ms latency. Acceptable for batch scheduling; irrelevant for real-time use cases.

### Risks

| Risk | Mitigation |
|---|---|
| FPL rate schedule changes without notice | Rates are scraped from FPL public API weekly; alert on change detection |
| ML confidence perpetually below 70% threshold | Static fallback engages automatically; alert fires to ops channel |
| Job deadline flush runs during peak window | Accepted — deadline integrity takes priority over cost optimization; log event for analysis |
| Scheduler outage during TOU window | SQS queue persists jobs; scheduler resumes on Lambda cold start |

### Accepted Tradeoffs

We accept ML pipeline operational overhead ($30–50/mo in infrastructure, quarterly
retraining) because the incremental savings over static-only scheduling ($15–20% per
billing cycle) compound materially at scale, and because the ML confidence signal
provides a natural circuit breaker that eliminates the over-scheduling failure mode.
