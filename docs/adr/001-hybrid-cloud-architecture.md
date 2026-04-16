# ADR-001: Hybrid Cloud Architecture

**Status:** Accepted
**Date:** 2026-04-01
**Deciders:** SunShift Architecture Team

---

## Context

Florida SMBs (5-50 employees) face two compounding risks that standard infrastructure
ignores:

1. **Hurricane risk** — Hurricane Milton (October 2024) caused 3.4M power outages in
   Tampa Bay alone. FEMA data shows 60% of small businesses never reopen after a major
   natural disaster. Most SMBs run on-premises hardware with no offsite replication.

2. **Electricity cost spikes** — Florida Power & Light (FPL) commercial TOU rates hit
   27.0¢/kWh during peak windows (12PM–9PM, summer), a 4.5x multiplier over the
   6.0¢/kWh off-peak rate. Compute-heavy workloads run 24/7 by default, burning money
   during the most expensive hours.

Three infrastructure approaches were evaluated:

| Approach | Description | Monthly Cost | Hurricane Safety | On-Prem Preservation |
|---|---|---|---|---|
| **Full Cloud (AWS Outposts)** | Managed hardware at customer site, full AWS control plane | $250K+ setup | Partial (hardware still on-site) | No |
| **On-Prem Only** | Traditional servers, no cloud failover | $0 cloud cost | None (58% backup failure rate) | Yes |
| **Hybrid (chosen)** | On-prem primary + cloud burst/failover on demand | $0–$150/mo cloud | Full (data evacuated before landfall) | Yes |

The full-cloud path (Outposts) prices out the entire SMB segment. On-prem-only leaves
businesses exposed to exactly the disasters they fear. The hybrid path matches the
customer's existing asset base — they already own servers — while adding cloud
resilience exactly when it matters.

---

## Decision

We adopt a **three-layer hybrid architecture**:

```
Layer 1 — On-Premises Agent (Python)
  └── Monitors local workload queue
  └── Encrypts data (AES-256-GCM, customer master key)
  └── Syncs to S3 via scheduled or event-driven trigger
  └── Managed by systemd watchdog (auto-restart on crash)

Layer 2 — Cloud Scheduler (AWS, us-east-2)
  └── FastAPI scheduler service
  └── EventBridge rules for TOU windows + hurricane triggers
  └── Lambda functions for workload execution
  └── S3 + KMS for encrypted storage

Layer 3 — Next.js Dashboard
  └── 3-state traffic light (GREEN / YELLOW / RED)
  └── Real-time cost savings display
  └── Hurricane alert banner (sourced from NOAA NHC API)
```

The on-prem agent is the only process that touches customer data directly. All cloud
communication happens over TLS 1.3. The dashboard presents operational state without
exposing raw infrastructure details to non-technical users.

We chose hybrid over full-cloud because:
- Eliminates $250K+ upfront Outposts cost (unacceptable for SMB segment)
- Preserves existing server investment (customers already own hardware)
- Delivers $100–150/mo in electricity savings via TOU scheduling
- Provides hurricane evacuation path that pure on-prem cannot

---

## Consequences

### Positive

- **Cost-preserving:** SMBs keep existing hardware; no forklift replacement
- **Electricity savings:** $100–150/mo by shifting batch workloads off TOU peak windows
- **Hurricane protection:** Cloud data copy survives even if on-prem hardware is
  physically destroyed
- **Incremental adoption:** Businesses can start with TOU scheduling and add hurricane
  shield later

### Negative

- **Agent reliability is critical:** If the on-prem Python agent crashes during a
  hurricane evacuation window, no backup occurs. Mitigation: systemd watchdog with
  auto-restart, health-check heartbeats every 60 seconds.
- **Two environments to monitor:** On-prem agent state + cloud scheduler state must be
  reconciled. Dashboard consolidates both but ops complexity is real.
- **Latency constraints:** Round-trip to Ohio (us-east-2) is ~35ms. This rules out
  real-time transactional workloads. SunShift only targets batch/async jobs
  (backups, reports, nightly ETL).

### Risks

| Risk | Mitigation |
|---|---|
| Agent crash during hurricane evacuation | systemd watchdog auto-restart; last-known-good checkpoint |
| Network outage during TOU window shift | Local job queue persists to disk; retries on reconnect |
| Customer runs real-time workload through SunShift | Onboarding wizard explicitly excludes latency-sensitive workloads |
| S3 sync failure mid-hurricane | S3 multipart upload with resume; EventBridge dead-letter queue |

### Accepted Tradeoffs

We accept the operational complexity of two environments because the alternative (pure
cloud) is economically unviable for the target segment, and pure on-prem leaves
customers with no disaster recovery path.
