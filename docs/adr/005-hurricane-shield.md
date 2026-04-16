# ADR-005: Hurricane Shield — Event-Driven Emergency Backup

**Status:** Accepted
**Date:** 2026-04-01
**Deciders:** SunShift Architecture Team

---

## Context

Tampa Bay is one of the highest-risk hurricane zones in the continental United States.
The National Hurricane Center (NHC) identifies Tampa Bay as having "one of the most
vulnerable storm surge environments in the country" due to the shallow, funnel-shaped
geography of the bay.

### Historical Impact Data

| Event | Year | Tampa Bay Impact | Power Outages | Business Impact |
|---|---|---|---|---|
| Hurricane Milton | 2024 | Direct hit, Category 3 landfall | 3.4M in Florida | $3B+ insured losses |
| Hurricane Ian | 2022 | South Florida direct, Tampa near miss | 2.6M | $109B total damage |
| Hurricane Irma | 2017 | Statewide impacts | 6.5M | $50B total damage |
| Hurricane Charley | 2004 | Punta Gorda, Tampa Bay near miss | 2M | $16B |

FEMA data: **60% of small businesses never reopen after a major natural disaster.**
The primary cause is not physical building damage — it is data loss and operational
continuity failure. A business whose QuickBooks database, client files, and email
archive survive on a cloud backup in Ohio can reopen from a hotel room.

### The Backup Failure Problem

Traditional SMB backup solutions fail precisely when most needed:

- **58% of traditional backups fail during actual disaster recovery** (Unitrends, 2023
  Backup and DR Survey)
- Common failure modes: backup media stored on-site (destroyed with hardware),
  tape backups never tested, cloud sync paused months ago by an IT change
- The "backup" that exists only in theory provides no actual recovery capability

SunShift's differentiation is **automated, verified, event-triggered backup** that
activates before a storm makes landfall — not after.

### Trigger Design Problem

Three trigger approaches were considered:

| Approach | Reliability | Cost | Accuracy |
|---|---|---|---|
| Manual trigger only | Low (requires human action during evacuation chaos) | None | Human judgment varies |
| Continuous real-time sync | High | High ($30–50/mo always-on infrastructure) | Overkill for non-storm periods |
| **Event-driven NOAA poll (chosen)** | High | Near-zero when idle | NHC advisory data is authoritative |

Continuous sync is the correct pattern for enterprises, but at SMB pricing ($99–199/mo)
it is not economically viable to run always-on replication infrastructure. Event-driven
polling costs near-zero between storms and activates automatically when the threat is
real.

---

## Decision

We implement an **EventBridge-scheduled NOAA NHC API polling system** with
distance-based trigger logic and natural-language dashboard alerts via Claude API.

### Trigger Architecture

```
EventBridge Rule: cron(0/30 * * * ? *)  ← every 30 minutes
  → Lambda: hurricane-monitor
      ├── Fetch NHC Active Advisories API
      │   URL: https://api.weather.gov/alerts/active?area=FL
      ├── Parse advisory JSON
      │   → Extract storm name, category, coordinates, track forecast
      ├── Distance calculation
      │   Tampa Bay reference: 27.9506°N, 82.4572°W
      │   Formula: Haversine distance (storm center → Tampa Bay)
      ├── Trigger logic:
      │   Category 1+ within 300 miles → FULL_BACKUP
      │   Tropical Storm within 200 miles → INCREMENTAL_BACKUP
      │   Tropical Depression within 150 miles → ALERT_ONLY
      │   No storm within range → NO_ACTION
      └── On trigger: publish to SNS → on-prem agent command queue
```

### Backup Command Flow

```
FULL_BACKUP trigger:
  1. SNS → SQS → on-prem agent via long-poll
  2. Agent: encrypt all customer-defined data directories (AES-256-GCM)
  3. Agent: upload to S3 us-east-2 with multipart (resume-capable)
  4. Agent: publish completion event to SQS response queue
  5. Lambda: update DynamoDB backup status record
  6. Dashboard: display RED alert with last-backup timestamp

INCREMENTAL_BACKUP trigger:
  1. Same flow as FULL_BACKUP but agent scans only files modified since last backup
  2. Faster completion time (15–30 min vs 2–4 hr for full backup)
  3. Designed for the 24–48 hour pre-landfall window when time is limited
```

### Natural-Language Alert (Claude API Integration)

The raw NHC advisory bulletin is dense technical language:

> "...THE CENTER OF TROPICAL STORM HELENE WAS LOCATED NEAR LATITUDE 24.1 NORTH,
> LONGITUDE 84.3 WEST. HELENE IS MOVING TOWARD THE NORTH-NORTHEAST NEAR 12 MPH
> (19 KM/H). A TURN TOWARD THE NORTH IS EXPECTED TODAY..."

This is opaque to a non-meteorologist SMB owner. The hurricane-monitor Lambda sends the
raw advisory to Claude API and requests a customer-facing summary:

```python
prompt = f"""
You are a disaster preparedness assistant for a Florida small business owner.
Summarize this NHC advisory in 2 sentences for a non-technical audience.
Include: storm name, current category, distance from Tampa Bay, and recommended action.
Advisory: {raw_advisory_text}
"""
```

Output displayed in dashboard alert banner:
> "Tropical Storm Helene is currently 280 miles from Tampa Bay and strengthening.
> SunShift has automatically started a full backup of your data — no action required."

### Cost Model

| Component | Cost (idle, no storm) | Cost (active storm week) |
|---|---|---|
| EventBridge rule | ~$0/mo | ~$0/mo |
| Lambda invocations (every 30 min) | ~$0.05/mo | ~$0.05/mo |
| NHC API calls | $0 (free public API) | $0 |
| S3 backup storage | ~$2–10/mo (existing data) | ~$2–10/mo |
| Claude API (alert generation) | $0 (no storms) | ~$0.10/event |
| **Total hurricane shield cost** | **~$0.05/mo** | **~$0.15/mo** |

The event-driven architecture delivers near-zero cost between hurricane seasons
(June–November), which is 7 months per year.

---

## Consequences

### Positive

- **Strongest emotional selling point:** "We start your backup automatically when a
  hurricane is coming" is a concrete, testable promise that addresses the exact fear
  SMBs have — being displaced during evacuation with no way to recover their data
- **Near-zero idle cost:** EventBridge + Lambda polling at 30-minute intervals costs
  under $0.10/month when no storms are active
- **Authoritative data source:** NHC advisories are the official US government source
  for tropical cyclone information; no third-party reliability dependency
- **Resume-capable uploads:** S3 multipart upload ensures a backup interrupted by
  power failure can resume when connectivity is restored
- **Natural-language alerts reduce panic:** SMB owners do not need to interpret storm
  track coordinates; Claude API translates to plain-English action items

### Negative

- **NOAA API dependency:** NHC advisory format has changed twice in the past 10 years.
  Advisory parser must be maintained and tested against format changes. Mitigation:
  integration test suite validates parser against 5 years of archived advisories.
- **30-minute polling gap:** A fast-moving storm could intensify significantly within a
  single 30-minute window. Mitigation: when a storm is within 400 miles, polling
  frequency escalates to 10 minutes (override EventBridge rule).
- **Agent must be online:** If the on-prem agent is offline when the backup command
  arrives (e.g., customer already lost power), the backup does not execute. This is an
  inherent limitation of hybrid architecture during power-outage scenarios. Mitigation:
  SunShift's marketing clearly states the service works best when started before power
  loss; incremental backups run nightly to minimize data loss window.

### Risks

| Risk | Mitigation |
|---|---|
| NHC advisory format change breaks parser | Weekly parser health check against live NHC feed; alert on parse failure |
| Customer already evacuated when storm intensifies | Last-backup timestamp shown in dashboard; nightly incremental minimizes exposure |
| S3 upload interrupted by power failure | Multipart upload with checkpoint; agent resumes on reconnect |
| False positive trigger (storm turns away) | Backup completes harmlessly; excess S3 cost is minimal ($0.02/GB) |
| Claude API latency delays dashboard alert | Alert generation is async; backup trigger does NOT wait for Claude response |

### Accepted Tradeoffs

We accept the 30-minute polling interval (vs. continuous streaming) and the agent
online requirement because the event-driven architecture reduces idle costs from
$30–50/month (continuous) to under $0.10/month, making hurricane protection
economically viable at SMB subscription pricing. The nightly incremental backup
cadence limits the worst-case data loss window to 24 hours even if the agent goes
offline before the emergency backup triggers.
