# ADR-002: AWS Ohio (us-east-2) as Cloud Destination

**Status:** Accepted
**Date:** 2026-04-01
**Deciders:** SunShift Architecture Team

---

## Context

SunShift's cloud destination must satisfy four requirements simultaneously:

1. **Geographic separation from Florida** — A cloud region that could itself be affected
   by a Gulf or Atlantic hurricane provides false safety. Tampa Bay sits at
   27.9506°N, 82.4572°W. Any viable region must be outside the hurricane belt.

2. **Low enough latency for async batch** — SunShift targets batch and async workloads
   (nightly ETL, backup jobs, report generation). Round-trip latency under 50ms is
   acceptable; real-time transactional workloads are explicitly out of scope.

3. **Cost parity or advantage** — SMBs are cost-sensitive. The cloud destination should
   not add meaningful cost premium over the lowest AWS pricing tier.

4. **AWS ecosystem compatibility** — The scheduler service relies on EventBridge,
   Lambda, S3, and KMS. These must be fully available in the selected region.

Five candidate regions were evaluated:

| Region | Distance from Tampa | Avg Latency | On-Demand t3.medium | Hurricane Risk | Notes |
|---|---|---|---|---|---|
| us-east-1 (N. Virginia) | ~750 mi | ~25ms | $0.0416/hr | Medium (Dorian 2019 reached VA coast) | Closest, slight hurricane exposure |
| **us-east-2 (Ohio)** | **~920 mi** | **~35ms** | **$0.0416/hr** | **None** | **Chosen** |
| us-west-2 (Oregon) | ~2,700 mi | ~70ms | $0.0416/hr | None (earthquake zone) | Latency borderline for sync ops |
| ca-central-1 (Canada) | ~1,400 mi | ~45ms | $0.0454/hr | None | 9% cost premium, cross-border data |
| eu-west-1 (Ireland) | ~4,700 mi | ~110ms | $0.0464/hr | None | Latency unacceptable, 12% premium |

All three US regions share the same t3.medium price ($0.0416/hr). Ohio's advantage over
Virginia is purely risk-based: Virginia sits at 37°N on the Atlantic seaboard and has
seen near-miss hurricane events (Florence 2018 made landfall at NC/VA border;
Dorian 2019 caused Category 1 conditions along the Virginia coast).

Ohio is landlocked at 40°N with no Atlantic exposure. It has never experienced a
hurricane or tropical storm event in recorded history.

---

## Decision

We designate **AWS us-east-2 (Ohio)** as the primary cloud destination for all
SunShift workload migration and backup operations.

Reasoning over the two closest competitors:

**Ohio vs. Virginia (us-east-1):**
- Same price tier ($0.0416/hr)
- Virginia latency advantage is only 10ms — negligible for async batch
- Virginia has documented Atlantic hurricane exposure
- Ohio provides a meaningful safety margin with no cost penalty

**Ohio vs. Oregon (us-west-2):**
- Same price tier ($0.0416/hr)
- Oregon latency (~70ms) is borderline for synchronous operations; Ohio (~35ms) is
  comfortably within range
- Oregon sits in an earthquake zone (Cascadia Subduction Zone); trading one natural
  disaster risk for another is not an acceptable mitigation

All required AWS services (EventBridge, Lambda, S3, KMS, EC2, IAM) are fully available
in us-east-2. There are no service gaps that would require multi-region workarounds.

Data transfer at SMB scale (typically 50–500 GB/backup cycle) costs $0.02/GB for
outbound from us-east-2, which is identical to all US regions. At a 100 GB backup,
cross-region transfer adds $2/cycle — negligible against $100–150/mo electricity
savings.

---

## Consequences

### Positive

- **Physically safe from Florida hurricanes:** Ohio's inland position at 40°N puts it
  outside every plausible Atlantic or Gulf hurricane track
- **Zero cost premium:** Identical pricing to us-east-1 eliminates budget justification
  friction with SMB customers
- **Full AWS service availability:** All EventBridge, Lambda, KMS, S3 primitives
  present; no workarounds required
- **Clear customer message:** "Your data lives in Ohio — safe from any Florida storm" is
  a crisp, testable claim

### Negative

- **10ms latency overhead vs. Virginia:** For the batch/async workloads SunShift
  targets, this is imperceptible. If a future product version adds real-time workloads,
  this tradeoff must be revisited.
- **Cross-region egress cost:** $0.02/GB applies when data moves from Ohio back to
  Florida. At SMB scale this is low ($2–10/restore cycle), but must be surfaced in
  pricing documentation.

### Risks

| Risk | Mitigation |
|---|---|
| AWS regional outage in us-east-2 | S3 Cross-Region Replication to us-east-1 as disaster-recovery tier (opt-in for premium tier) |
| Customer data residency concerns | All data remains in US (us-east-2). HIPAA customers receive explicit BAA scoped to us-east-2 |
| Latency spikes during peak AWS load | Batch jobs queued locally first; scheduler retries on timeout |

### Accepted Tradeoffs

We accept the 10ms latency increase over us-east-1 in exchange for zero hurricane risk
at the cloud destination. For SunShift's batch-and-async workload profile, 35ms
round-trip is operationally equivalent to 25ms.
