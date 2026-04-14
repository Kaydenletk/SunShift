# SunShift Infrastructure

Terraform IaC for deploying SunShift to AWS.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AWS Cloud (us-east-2)                                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  VPC (10.0.0.0/16)                                   │  │
│  │                                                       │  │
│  │  ┌─────────────────┐    ┌─────────────────────────┐  │  │
│  │  │  Public Subnets │    │    Private Subnets      │  │  │
│  │  │  ┌───────────┐  │    │  ┌─────────────────┐    │  │  │
│  │  │  │    ALB    │──┼────┼──│   ECS Fargate   │    │  │  │
│  │  │  └───────────┘  │    │  │   (FastAPI)     │    │  │  │
│  │  └─────────────────┘    │  └─────────────────┘    │  │  │
│  │                         │          │              │  │  │
│  │  ┌─────────────────┐    │          ▼              │  │  │
│  │  │  NAT Gateway    │◄───┤  ┌─────────────────┐    │  │  │
│  │  └─────────────────┘    │  │   Lambda Fns    │    │  │  │
│  │                         │  └─────────────────┘    │  │  │
│  │                         └─────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │   S3    │  │  DynamoDB   │  │   EventBridge       │    │
│  │ Buckets │  │   Table     │  │   (Event Bus)       │    │
│  └─────────┘  └─────────────┘  └──────────────────────┘    │
│                                                             │
│  ┌─────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │   KMS   │  │ CloudWatch  │  │   Secrets Manager   │    │
│  │  Keys   │  │ Dashboard   │  │                     │    │
│  └─────────┘  └─────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.9.0
- AWS account with appropriate permissions

## Quick Start

### 1. Initialize Backend (First Time Only)

```bash
cd infra/scripts
./init-backend.sh
```

Update `environments/dev/backend.tf` with the bucket name printed by the script.

### 2. Deploy to Dev

```bash
./scripts/deploy.sh dev init
./scripts/deploy.sh dev plan
./scripts/deploy.sh dev apply
```

### 3. View Outputs

```bash
./scripts/deploy.sh dev output
```

## Modules

| Module | Description |
|--------|-------------|
| `networking` | VPC, subnets, NAT Gateway, route tables |
| `security` | KMS keys, security groups, IAM roles |
| `storage` | S3 buckets with encryption and lifecycle policies |
| `database` | DynamoDB single-table design |
| `ecs` | ECS Fargate cluster, task definition, ALB |
| `events` | EventBridge rules and DLQ |
| `monitoring` | CloudWatch dashboard and alarms |

## Environment Variables

Required environment variables for deployment:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-2"

# Optional: API keys (can also be set in Secrets Manager)
export TF_VAR_openweathermap_api_key="..."
export TF_VAR_eia_api_key="..."
export TF_VAR_anthropic_api_key="..."
export TF_VAR_gemini_api_key="..."
```

## Costs

Estimated monthly costs for dev environment:

| Service | Usage | Cost |
|---------|-------|------|
| S3 (10GB) | Demo data | ~$0.23 |
| DynamoDB (on-demand) | Light usage | ~$1-2 |
| ECS Fargate (0.25 vCPU, 0.5GB) | 24/7 | ~$9 |
| NAT Gateway | Data transfer | ~$3-5 |
| CloudWatch | Logs + metrics | ~$3 |
| **Total** | | **~$15-20/month** |

## Security

- All S3 buckets have public access blocked
- Customer data encrypted with per-environment KMS keys
- IAM roles follow least-privilege principle
- Security groups restrict traffic to necessary ports only
