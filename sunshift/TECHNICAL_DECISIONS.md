# Technical Decisions

## Executive Summary

SunShift is a hybrid cloud orchestration system designed for Florida SMBs facing two challenges: volatile electricity pricing and hurricane risk. This document explains the key architectural decisions and trade-offs made during development.

The system uses a **Prophet + XGBoost ensemble** for price prediction, achieving ~15% higher accuracy than either model alone. Infrastructure runs on **AWS ECS Fargate** for zero-ops container management, with **Terraform** enabling reproducible deployments across environments. Hurricane alerts leverage **Google Gemini API** with Anthropic Claude as fallback for reliability during actual storm events.

**Key constraints that shaped decisions:**
- Budget: ~$15-20/month infrastructure cost for dev environment
- HIPAA-ready architecture (for future healthcare segment expansion)
- Florida-specific: FPL TOU pricing, hurricane season (June-November)
- Portfolio project: emphasize modern practices over legacy compatibility

---

## ADR-001: Prophet + XGBoost Ensemble for Price Prediction

### Status
Accepted

### Context
We need to predict FPL TOU electricity prices 24 hours ahead to schedule optimal migration windows. The predictions must account for:
- Daily seasonality (peak hours 12 PM - 9 PM)
- Weekly patterns (weekday vs weekend usage)
- Weather correlation (AC load during heat waves)
- Holiday effects (reduced commercial usage)

### Decision
Use Facebook Prophet for trend and seasonality decomposition, combined with XGBoost for residual correction. Prophet handles the time series fundamentals while XGBoost captures non-linear patterns Prophet misses.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Prophet only | Simple, interpretable, handles seasonality well | Misses non-linear patterns, weather correlations |
| XGBoost only | Handles complexity, feature interactions | Requires manual feature engineering for time |
| LSTM/Transformer | State-of-the-art accuracy potential | Overkill for this data volume, harder to explain |
| ARIMA | Classical, well-understood | Poor with multiple seasonality patterns |

### Consequences
- **Positive:** ~15% improvement in prediction accuracy over Prophet alone
- **Positive:** Interpretable decomposition from Prophet aids debugging
- **Negative:** Two models to maintain and tune
- **Negative:** Training pipeline more complex than single-model approach

---

## ADR-002: Single-Table DynamoDB Design

### Status
Accepted

### Context
We need to store workload states, migration history, and prediction cache with low-latency access. The access patterns are:
- Get current state of all workloads (frequent)
- Get migration history for a date range (occasional)
- Get cached predictions for next 24 hours (frequent)
- Write new predictions hourly (scheduled)

### Decision
Use DynamoDB with single-table design pattern. Partition key structure:
- `WL#<workload-id>` — Workload state records
- `MIG#<date>#<id>` — Migration history
- `PRED#<date>#<hour>` — Prediction cache

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| PostgreSQL RDS | Relational queries, familiar SQL | Higher cost (~$15/month min), more operational overhead |
| Aurora Serverless v2 | Auto-scaling, PostgreSQL compatible | Cold start latency, minimum cost higher |
| Redis ElastiCache | Ultra-fast reads | Persistence concerns, cost for small workloads |
| SQLite (local) | Zero cost, simple | Not suitable for distributed access |

### Consequences
- **Positive:** Pay-per-request pricing fits budget (~$2/month for dev)
- **Positive:** Millisecond latency for all access patterns
- **Negative:** Denormalized data requires careful access pattern design
- **Negative:** No ad-hoc SQL queries; must design GSIs upfront

---

## ADR-003: Gemini API with Claude Fallback

### Status
Accepted

### Context
Hurricane alerts need AI-generated executive summaries that are actionable and appropriately urgent. The alerts must be reliable during actual hurricane events when API availability may be impacted by infrastructure stress.

### Decision
Use Google Gemini as primary LLM (lower cost, good quality) with Anthropic Claude as fallback (higher quality, higher cost). Implement automatic failover with exponential backoff.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| OpenAI GPT-4 | Most widely used, extensive docs | Higher cost per token, rate limits |
| Local LLM (Llama) | No API dependency, privacy | Compute requirements don't fit budget |
| Template-based | Simple, 100% reliable, zero cost | Less dynamic, can't adapt to storm specifics |
| Claude only | Highest quality output | Higher cost, single point of failure |

### Consequences
- **Positive:** Cost optimization (Gemini ~60% cheaper than Claude)
- **Positive:** Reliability through redundancy
- **Negative:** Dual API key management
- **Negative:** Slight latency on fallback scenarios

---

## ADR-004: ECS Fargate over EC2

### Status
Accepted

### Context
We need to run the FastAPI backend containers with minimal operational overhead. The workload is relatively small (2-3 containers) but must be reliable and cost-effective.

### Decision
Use AWS ECS Fargate for serverless container execution. No cluster management required.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| ECS on EC2 | More control, potentially cheaper at scale | Instance management, capacity planning |
| EKS (Kubernetes) | Industry standard, portable | Complexity overkill for 2-3 services, ~$70/month for control plane |
| Lambda | True serverless, pay-per-invocation | Cold starts problematic for WebSocket, 15-min timeout |
| Bare EC2 | Full control, cheapest raw compute | Full operational responsibility |

### Consequences
- **Positive:** Zero server management
- **Positive:** Per-second billing aligns with variable workload
- **Positive:** Built-in integration with ALB, CloudWatch
- **Negative:** Slight cold start on scale-from-zero (~10-30 seconds)
- **Negative:** More expensive than EC2 at high utilization

---

## ADR-005: EventBridge for Scheduling

### Status
Accepted

### Context
We need to trigger prediction updates (hourly), migration checks (every 15 minutes during peak hours), and health checks on a schedule.

### Decision
Use AWS EventBridge Scheduler for cron-based invocations of ECS tasks and Lambda functions.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| CloudWatch Events | Same underlying service | Legacy naming, migrating to EventBridge |
| Step Functions | Visual workflows, complex orchestration | Overkill for simple cron jobs |
| In-app scheduler (APScheduler) | Self-contained, no AWS dependency | Requires always-on instance, single point of failure |
| Kubernetes CronJobs | Native if using K8s | We're not using Kubernetes |

### Consequences
- **Positive:** Native AWS integration, reliable invocation
- **Positive:** No additional compute cost (scheduler is free, pay for targets)
- **Negative:** Slight latency for cold starts on Fargate targets
- **Negative:** Debugging requires CloudWatch Logs correlation

---

## ADR-006: Terraform Modules over CDK

### Status
Accepted

### Context
We need reproducible infrastructure deployment. The infrastructure includes VPC, ECS, DynamoDB, S3, EventBridge, ALB, and CloudWatch resources.

### Decision
Use Terraform with modular structure (8 modules: networking, security, storage, database, ecs, events, monitoring, and root).

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| AWS CDK | TypeScript, type-safe, higher abstraction | Learning curve, CloudFormation underneath |
| CloudFormation | Native AWS, no state management | Verbose YAML/JSON, harder to modularize |
| Pulumi | Multi-language, modern DX | Smaller ecosystem than Terraform |
| AWS Console (manual) | Quick prototyping | Not reproducible, configuration drift |

### Consequences
- **Positive:** Industry-standard IaC, widely understood
- **Positive:** Module reusability across environments
- **Positive:** Extensive provider ecosystem
- **Negative:** State management required (S3 + DynamoDB for locking)
- **Negative:** HCL learning curve vs. general-purpose languages

---

## Trade-offs Considered But Rejected

### Multi-Region Deployment
**Why not:** Budget constraints (~$15-20/month target). Single region (us-east-2 Ohio) is sufficient for demo/portfolio purposes. Multi-region would add ~$30/month for cross-region replication and additional load balancers.

### Kubernetes (EKS)
**Why not:** Operational complexity unjustified for 2-3 services. EKS control plane alone costs ~$70/month. ECS Fargate provides adequate container orchestration without cluster management overhead.

### Real-time Streaming (Kinesis)
**Why not:** Batch predictions at hourly intervals are sufficient for electricity pricing that changes on predictable TOU schedules. Real-time streaming would add cost ($25+/month for Kinesis) without proportional value.

### GraphQL API
**Why not:** REST is adequate for current use cases (CRUD operations + prediction endpoints). GraphQL adds complexity for simple request-response patterns. Would reconsider if frontend requirements become more complex with nested data fetching.

### Redis for Caching
**Why not:** DynamoDB with DAX or simple in-memory caching is sufficient for prediction cache. ElastiCache minimum is ~$12/month, which represents a significant portion of the budget for marginal latency improvement.

---

## Appendix: Cost Breakdown

| Resource | Service | Monthly Estimate |
|----------|---------|------------------|
| Compute | ECS Fargate (2 tasks, 0.25 vCPU, 0.5GB) | ~$8 |
| Database | DynamoDB (on-demand, <1GB) | ~$2 |
| Storage | S3 (<1GB) | ~$0.50 |
| Networking | ALB | ~$5 |
| Monitoring | CloudWatch (basic) | ~$2 |
| **Total** | | **~$17.50** |

*Estimates based on us-east-2 pricing as of April 2026. Actual costs may vary based on usage patterns.*
