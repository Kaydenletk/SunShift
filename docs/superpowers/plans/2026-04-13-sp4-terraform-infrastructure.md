# SP4: Terraform Infrastructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy SunShift to AWS using Terraform IaC — VPC, ECS Fargate for FastAPI backend, S3 buckets, DynamoDB, EventBridge, Lambda, KMS encryption, CloudWatch monitoring, and IAM roles with least-privilege security.

**Architecture:** Event-driven serverless architecture on AWS us-east-2 (Ohio). ECS Fargate runs FastAPI backend, Lambda handles hurricane alerts and scheduled tasks, EventBridge orchestrates events, S3 stores customer data and ML artifacts, DynamoDB serves as single-table datastore, KMS provides encryption, CloudWatch monitors everything.

**Tech Stack:** Terraform 1.9+, AWS Provider 5.x, modular design with environments (dev/staging/prod)

**Spec:** `docs/superpowers/specs/2026-04-13-sunshift-mvp-design.md`

---

## File Structure

```
sunshift/
├── infra/
│   ├── modules/
│   │   ├── networking/
│   │   │   ├── main.tf              # VPC, subnets, NAT, IGW
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── ecs/
│   │   │   ├── main.tf              # ECS cluster, task def, service, ALB
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── storage/
│   │   │   ├── main.tf              # S3 buckets, lifecycle policies
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── database/
│   │   │   ├── main.tf              # DynamoDB table, GSIs
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── lambda/
│   │   │   ├── main.tf              # Lambda functions, IAM roles
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── events/
│   │   │   ├── main.tf              # EventBridge rules, targets
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── security/
│   │   │   ├── main.tf              # KMS keys, security groups, IAM
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── monitoring/
│   │       ├── main.tf              # CloudWatch dashboards, alarms
│   │       ├── variables.tf
│   │       └── outputs.tf
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf
│   │   └── prod/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       ├── terraform.tfvars
│   │       └── backend.tf
│   └── scripts/
│       ├── init-backend.sh          # Create S3 backend + DynamoDB lock table
│       └── deploy.sh                # Deployment helper script
├── .github/
│   └── workflows/
│       └── terraform.yml            # CI/CD pipeline
└── tests/
    └── infra/
        └── test_terraform.py        # Terraform validation tests
```

---

### Task 0: Project Scaffolding + Terraform Backend

**Goal:** Set up Terraform project structure with S3 backend for state storage and DynamoDB for state locking. Create base configuration files.

**Files:**
- Create: `sunshift/infra/modules/.gitkeep`
- Create: `sunshift/infra/environments/dev/backend.tf`
- Create: `sunshift/infra/environments/dev/versions.tf`
- Create: `sunshift/infra/environments/dev/variables.tf`
- Create: `sunshift/infra/environments/dev/terraform.tfvars`
- Create: `sunshift/infra/scripts/init-backend.sh`

**Acceptance Criteria:**
- [ ] `init-backend.sh` creates S3 bucket and DynamoDB table for Terraform state
- [ ] `terraform init` succeeds in environments/dev
- [ ] State file stored in S3 with encryption
- [ ] State locking via DynamoDB

**Verify:** `cd sunshift/infra/environments/dev && terraform init` → succeeds

**Steps:**

- [ ] **Step 1: Create init-backend.sh script**

Create `sunshift/infra/scripts/init-backend.sh`:

```bash
#!/bin/bash
set -euo pipefail

REGION="${AWS_REGION:-us-east-2}"
BUCKET_NAME="sunshift-terraform-state-$(aws sts get-caller-identity --query Account --output text)"
TABLE_NAME="sunshift-terraform-locks"

echo "Creating S3 bucket for Terraform state: $BUCKET_NAME"
aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION" 2>/dev/null || true

aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration '{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }'

echo "Creating DynamoDB table for state locking: $TABLE_NAME"
aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" 2>/dev/null || true

echo ""
echo "✓ Terraform backend ready!"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  DynamoDB Table: $TABLE_NAME"
echo ""
echo "Update your backend.tf with:"
echo "  bucket         = \"$BUCKET_NAME\""
echo "  dynamodb_table = \"$TABLE_NAME\""
```

- [ ] **Step 2: Create versions.tf with provider requirements**

Create `sunshift/infra/environments/dev/versions.tf`:

```hcl
terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "SunShift"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

- [ ] **Step 3: Create backend.tf for remote state**

Create `sunshift/infra/environments/dev/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "sunshift-terraform-state-ACCOUNT_ID"  # Replace after init-backend.sh
    key            = "dev/terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
    dynamodb_table = "sunshift-terraform-locks"
  }
}
```

- [ ] **Step 4: Create variables.tf**

Create `sunshift/infra/environments/dev/variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
  default     = "sunshift"
}

# VPC
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b"]
}

# ECS
variable "ecs_cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Fargate task memory in MB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

# API Keys (sensitive)
variable "openweathermap_api_key" {
  description = "OpenWeatherMap API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "eia_api_key" {
  description = "EIA API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic Claude API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "gemini_api_key" {
  description = "Google Gemini API key"
  type        = string
  sensitive   = true
  default     = ""
}
```

- [ ] **Step 5: Create terraform.tfvars**

Create `sunshift/infra/environments/dev/terraform.tfvars`:

```hcl
aws_region   = "us-east-2"
environment  = "dev"
project_name = "sunshift"

vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-2a", "us-east-2b"]

ecs_cpu           = 256
ecs_memory        = 512
ecs_desired_count = 1

# API keys should be provided via environment variables or AWS Secrets Manager
# TF_VAR_openweathermap_api_key=xxx
# TF_VAR_eia_api_key=xxx
# TF_VAR_anthropic_api_key=xxx
# TF_VAR_gemini_api_key=xxx
```

- [ ] **Step 6: Create directory structure**

```bash
mkdir -p sunshift/infra/modules/{networking,ecs,storage,database,lambda,events,security,monitoring}
mkdir -p sunshift/infra/environments/{dev,prod}
mkdir -p sunshift/infra/scripts
touch sunshift/infra/modules/.gitkeep
chmod +x sunshift/infra/scripts/init-backend.sh
```

- [ ] **Step 7: Commit**

```bash
git add sunshift/infra/
git commit -m "feat(sp4): Terraform project scaffolding + S3 backend + state locking"
```

---

### Task 1: Networking Module — VPC, Subnets, NAT Gateway

**Goal:** Create VPC with public/private subnets, Internet Gateway, NAT Gateway, and route tables for ECS Fargate deployment.

**Files:**
- Create: `sunshift/infra/modules/networking/main.tf`
- Create: `sunshift/infra/modules/networking/variables.tf`
- Create: `sunshift/infra/modules/networking/outputs.tf`

**Acceptance Criteria:**
- [ ] VPC with configurable CIDR block
- [ ] 2 public subnets (for ALB)
- [ ] 2 private subnets (for ECS Fargate)
- [ ] Internet Gateway for public subnets
- [ ] NAT Gateway for private subnet outbound access
- [ ] Route tables correctly configured
- [ ] Tags follow naming convention

**Verify:** `terraform validate` passes, `terraform plan` shows VPC resources

**Steps:**

- [ ] **Step 1: Create networking module variables**

Create `sunshift/infra/modules/networking/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway (cost saving for dev)"
  type        = bool
  default     = true
}
```

- [ ] **Step 2: Create networking module main.tf**

Create `sunshift/infra/modules/networking/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  az_count    = length(var.availability_zones)
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = local.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name_prefix}-public-${var.availability_zones[count.index]}"
    Type = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${local.name_prefix}-private-${var.availability_zones[count.index]}"
    Type = "private"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : local.az_count) : 0
  domain = "vpc"

  tags = {
    Name = "${local.name_prefix}-nat-eip-${count.index}"
  }

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : local.az_count) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${local.name_prefix}-nat-${count.index}"
  }

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${local.name_prefix}-public-rt"
  }
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count = local.az_count

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Route Tables
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : local.az_count) : 1
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[var.single_nat_gateway ? 0 : count.index].id
    }
  }

  tags = {
    Name = "${local.name_prefix}-private-rt-${count.index}"
  }
}

# Private Route Table Associations
resource "aws_route_table_association" "private" {
  count = local.az_count

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[var.single_nat_gateway ? 0 : count.index].id
}
```

- [ ] **Step 3: Create networking module outputs**

Create `sunshift/infra/modules/networking/outputs.tf`:

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/networking && terraform init && terraform validate
```

Expected: Success

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/networking/
git commit -m "feat(sp4): networking module — VPC, subnets, NAT Gateway, route tables"
```

---

### Task 2: Security Module — KMS, Security Groups, IAM Roles

**Goal:** Create KMS keys for encryption, security groups for ECS/ALB, and IAM roles with least-privilege policies.

**Files:**
- Create: `sunshift/infra/modules/security/main.tf`
- Create: `sunshift/infra/modules/security/variables.tf`
- Create: `sunshift/infra/modules/security/outputs.tf`

**Acceptance Criteria:**
- [ ] KMS key for S3 customer data encryption
- [ ] KMS key for DynamoDB encryption
- [ ] Security group for ALB (80, 443 inbound)
- [ ] Security group for ECS tasks (ALB only)
- [ ] IAM role for ECS task execution
- [ ] IAM role for ECS tasks (S3, DynamoDB, Secrets Manager access)
- [ ] IAM role for Lambda functions
- [ ] All policies follow least-privilege principle

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create security module variables**

Create `sunshift/infra/modules/security/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for security groups"
  type        = string
}

variable "vpc_cidr_block" {
  description = "VPC CIDR block for internal access"
  type        = string
}

variable "s3_bucket_arns" {
  description = "List of S3 bucket ARNs for IAM policies"
  type        = list(string)
  default     = []
}

variable "dynamodb_table_arn" {
  description = "DynamoDB table ARN for IAM policies"
  type        = string
  default     = ""
}

variable "kms_deletion_window_days" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}
```

- [ ] **Step 2: Create security module main.tf**

Create `sunshift/infra/modules/security/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# KMS Key for Customer Data (S3)
resource "aws_kms_key" "customer_data" {
  description             = "KMS key for SunShift customer data encryption"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true

  tags = {
    Name = "${local.name_prefix}-customer-data-key"
  }
}

resource "aws_kms_alias" "customer_data" {
  name          = "alias/${local.name_prefix}-customer-data"
  target_key_id = aws_kms_key.customer_data.key_id
}

# KMS Key for Application Secrets
resource "aws_kms_key" "app_secrets" {
  description             = "KMS key for SunShift application secrets"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true

  tags = {
    Name = "${local.name_prefix}-app-secrets-key"
  }
}

resource "aws_kms_alias" "app_secrets" {
  name          = "alias/${local.name_prefix}-app-secrets"
  target_key_id = aws_kms_key.app_secrets.key_id
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-alb-sg"
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name_prefix}-ecs-tasks-sg"
  description = "Security group for ECS Fargate tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "From ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-ecs-tasks-sg"
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-task-execution"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager access
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name = "${local.name_prefix}-ecs-task-execution-secrets"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:${local.name_prefix}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = aws_kms_key.app_secrets.arn
      }
    ]
  })
}

# IAM Role for ECS Tasks (application runtime)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-task"
  }
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${local.name_prefix}-ecs-task-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = concat(
          var.s3_bucket_arns,
          [for arn in var.s3_bucket_arns : "${arn}/*"]
        )
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = var.dynamodb_table_arn != "" ? [
          var.dynamodb_table_arn,
          "${var.dynamodb_table_arn}/index/*"
        ] : []
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.customer_data.arn
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Role for Lambda Functions
resource "aws_iam_role" "lambda_execution" {
  name = "${local.name_prefix}-lambda-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${local.name_prefix}-lambda-execution"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_custom" {
  name = "${local.name_prefix}-lambda-custom"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = concat(
          var.s3_bucket_arns,
          [for arn in var.s3_bucket_arns : "${arn}/*"]
        )
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query"
        ]
        Resource = var.dynamodb_table_arn != "" ? [var.dynamodb_table_arn] : []
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:${local.name_prefix}-*"
      }
    ]
  })
}
```

- [ ] **Step 3: Create security module outputs**

Create `sunshift/infra/modules/security/outputs.tf`:

```hcl
output "kms_customer_data_key_arn" {
  description = "ARN of KMS key for customer data"
  value       = aws_kms_key.customer_data.arn
}

output "kms_customer_data_key_id" {
  description = "ID of KMS key for customer data"
  value       = aws_kms_key.customer_data.key_id
}

output "kms_app_secrets_key_arn" {
  description = "ARN of KMS key for app secrets"
  value       = aws_kms_key.app_secrets.arn
}

output "alb_security_group_id" {
  description = "Security group ID for ALB"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

output "lambda_execution_role_arn" {
  description = "ARN of Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/security && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/security/
git commit -m "feat(sp4): security module — KMS keys, security groups, IAM roles with least-privilege"
```

---

### Task 3: Storage Module — S3 Buckets with Lifecycle Policies

**Goal:** Create S3 buckets for customer data, ML artifacts, raw data, and audit logs with appropriate encryption and lifecycle policies.

**Files:**
- Create: `sunshift/infra/modules/storage/main.tf`
- Create: `sunshift/infra/modules/storage/variables.tf`
- Create: `sunshift/infra/modules/storage/outputs.tf`

**Acceptance Criteria:**
- [ ] 4 S3 buckets: customer-data, ml-artifacts, raw-data, audit-logs
- [ ] Customer data bucket with KMS encryption
- [ ] Audit logs bucket with Object Lock (HIPAA compliance)
- [ ] Lifecycle policies: raw-data → Intelligent-Tiering, customer-data → Glacier after 1 year
- [ ] Public access blocked on all buckets
- [ ] Versioning enabled

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create storage module variables**

Create `sunshift/infra/modules/storage/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for customer data encryption"
  type        = string
}

variable "enable_audit_log_lock" {
  description = "Enable Object Lock for audit logs (HIPAA compliance)"
  type        = bool
  default     = false
}

variable "customer_data_retention_days" {
  description = "Days before transitioning customer data to Glacier"
  type        = number
  default     = 365
}
```

- [ ] **Step 2: Create storage module main.tf**

Create `sunshift/infra/modules/storage/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Customer Data Bucket (KMS encrypted)
resource "aws_s3_bucket" "customer_data" {
  bucket = "${local.name_prefix}-customer-data"

  tags = {
    Name     = "${local.name_prefix}-customer-data"
    DataType = "customer"
    HIPAA    = "true"
  }
}

resource "aws_s3_bucket_versioning" "customer_data" {
  bucket = aws_s3_bucket.customer_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "customer_data" {
  bucket = aws_s3_bucket.customer_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "customer_data" {
  bucket = aws_s3_bucket.customer_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "customer_data" {
  bucket = aws_s3_bucket.customer_data.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    transition {
      days          = var.customer_data_retention_days
      storage_class = "GLACIER"
    }
  }
}

# ML Artifacts Bucket
resource "aws_s3_bucket" "ml_artifacts" {
  bucket = "${local.name_prefix}-ml-artifacts"

  tags = {
    Name     = "${local.name_prefix}-ml-artifacts"
    DataType = "ml"
  }
}

resource "aws_s3_bucket_versioning" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Raw Data Bucket (Intelligent-Tiering)
resource "aws_s3_bucket" "raw_data" {
  bucket = "${local.name_prefix}-raw-data"

  tags = {
    Name     = "${local.name_prefix}-raw-data"
    DataType = "raw"
  }
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_intelligent_tiering_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  name   = "entire-bucket"

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }
}

# Audit Logs Bucket (HIPAA compliance)
resource "aws_s3_bucket" "audit_logs" {
  bucket = "${local.name_prefix}-audit-logs"

  object_lock_enabled = var.enable_audit_log_lock

  tags = {
    Name     = "${local.name_prefix}-audit-logs"
    DataType = "audit"
    HIPAA    = "true"
  }
}

resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    id     = "archive-after-7-years"
    status = "Enabled"

    transition {
      days          = 2555  # 7 years
      storage_class = "DEEP_ARCHIVE"
    }
  }
}
```

- [ ] **Step 3: Create storage module outputs**

Create `sunshift/infra/modules/storage/outputs.tf`:

```hcl
output "customer_data_bucket_name" {
  description = "Name of customer data S3 bucket"
  value       = aws_s3_bucket.customer_data.id
}

output "customer_data_bucket_arn" {
  description = "ARN of customer data S3 bucket"
  value       = aws_s3_bucket.customer_data.arn
}

output "ml_artifacts_bucket_name" {
  description = "Name of ML artifacts S3 bucket"
  value       = aws_s3_bucket.ml_artifacts.id
}

output "ml_artifacts_bucket_arn" {
  description = "ARN of ML artifacts S3 bucket"
  value       = aws_s3_bucket.ml_artifacts.arn
}

output "raw_data_bucket_name" {
  description = "Name of raw data S3 bucket"
  value       = aws_s3_bucket.raw_data.id
}

output "raw_data_bucket_arn" {
  description = "ARN of raw data S3 bucket"
  value       = aws_s3_bucket.raw_data.arn
}

output "audit_logs_bucket_name" {
  description = "Name of audit logs S3 bucket"
  value       = aws_s3_bucket.audit_logs.id
}

output "audit_logs_bucket_arn" {
  description = "ARN of audit logs S3 bucket"
  value       = aws_s3_bucket.audit_logs.arn
}

output "all_bucket_arns" {
  description = "List of all S3 bucket ARNs"
  value = [
    aws_s3_bucket.customer_data.arn,
    aws_s3_bucket.ml_artifacts.arn,
    aws_s3_bucket.raw_data.arn,
    aws_s3_bucket.audit_logs.arn
  ]
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/storage && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/storage/
git commit -m "feat(sp4): storage module — S3 buckets with KMS encryption, lifecycle policies, HIPAA compliance"
```

---

### Task 4: Database Module — DynamoDB Single-Table Design

**Goal:** Create DynamoDB table with single-table design pattern, GSIs for access patterns, TTL for automatic expiration, and on-demand billing.

**Files:**
- Create: `sunshift/infra/modules/database/main.tf`
- Create: `sunshift/infra/modules/database/variables.tf`
- Create: `sunshift/infra/modules/database/outputs.tf`

**Acceptance Criteria:**
- [ ] DynamoDB table with partition key (PK) and sort key (SK)
- [ ] GSI for location-based queries
- [ ] TTL attribute for automatic data expiration
- [ ] On-demand billing mode
- [ ] Point-in-time recovery enabled

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create database module variables**

Create `sunshift/infra/modules/database/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery for DynamoDB"
  type        = bool
  default     = true
}

variable "billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}
```

- [ ] **Step 2: Create database module main.tf**

Create `sunshift/infra/modules/database/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  table_name  = "${local.name_prefix}-main"
}

resource "aws_dynamodb_table" "main" {
  name         = local.table_name
  billing_mode = var.billing_mode
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # GSI for location-based queries
  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  # TTL for automatic data expiration
  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  tags = {
    Name = local.table_name
  }
}
```

- [ ] **Step 3: Create database module outputs**

Create `sunshift/infra/modules/database/outputs.tf`:

```hcl
output "table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.main.name
}

output "table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.main.arn
}

output "table_id" {
  description = "DynamoDB table ID"
  value       = aws_dynamodb_table.main.id
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/database && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/database/
git commit -m "feat(sp4): database module — DynamoDB single-table design with GSI, TTL, PITR"
```

---

### Task 5: ECS Module — Fargate Cluster, Task Definition, ALB

**Goal:** Create ECS Fargate cluster with task definition, service, Application Load Balancer, and target group for FastAPI backend deployment.

**Files:**
- Create: `sunshift/infra/modules/ecs/main.tf`
- Create: `sunshift/infra/modules/ecs/variables.tf`
- Create: `sunshift/infra/modules/ecs/outputs.tf`

**Acceptance Criteria:**
- [ ] ECS cluster with Fargate capacity provider
- [ ] Task definition with FastAPI container
- [ ] Application Load Balancer with health checks
- [ ] ECS service with auto-scaling (optional)
- [ ] CloudWatch log group for container logs
- [ ] Environment variables from Secrets Manager

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create ECS module variables**

Create `sunshift/infra/modules/ecs/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security group ID for ALB"
  type        = string
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of ECS task role"
  type        = string
}

variable "cpu" {
  description = "Fargate task CPU units"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Fargate task memory in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "container_image" {
  description = "Docker image for FastAPI container"
  type        = string
  default     = "python:3.12-slim"
}

variable "container_port" {
  description = "Container port for FastAPI"
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/health"
}

variable "environment_variables" {
  description = "Environment variables for container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secrets from Secrets Manager (name -> secret ARN)"
  type        = map(string)
  default     = {}
}
```

- [ ] **Step 2: Create ECS module main.tf**

Create `sunshift/infra/modules/ecs/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = 30

  tags = {
    Name = "${local.name_prefix}-ecs-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${local.name_prefix}-cluster"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "prod"

  tags = {
    Name = "${local.name_prefix}-alb"
  }
}

resource "aws_lb_target_group" "main" {
  name        = "${local.name_prefix}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${local.name_prefix}-tg"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = "${local.name_prefix}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = var.container_image

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        for key, value in var.environment_variables : {
          name  = key
          value = value
        }
      ]

      secrets = [
        for name, arn in var.secrets : {
          name      = name
          valueFrom = arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "api"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}${var.health_check_path} || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-api"
  }
}

data "aws_region" "current" {}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "${local.name_prefix}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = "api"
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name = "${local.name_prefix}-api"
  }
}
```

- [ ] **Step 3: Create ECS module outputs**

Create `sunshift/infra/modules/ecs/outputs.tf`:

```hcl
output "cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.main.name
}

output "task_definition_arn" {
  description = "ECS task definition ARN"
  value       = aws_ecs_task_definition.main.arn
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "ALB zone ID"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "ALB ARN"
  value       = aws_lb.main.arn
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = aws_lb_target_group.main.arn
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ecs.name
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/ecs && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/ecs/
git commit -m "feat(sp4): ECS module — Fargate cluster, task definition, ALB, health checks"
```

---

### Task 6: Events Module — EventBridge Rules

**Goal:** Create EventBridge event bus and rules for NOAA alerts, TOU schedule triggers, and ML prediction events.

**Files:**
- Create: `sunshift/infra/modules/events/main.tf`
- Create: `sunshift/infra/modules/events/variables.tf`
- Create: `sunshift/infra/modules/events/outputs.tf`

**Acceptance Criteria:**
- [ ] Custom EventBridge event bus
- [ ] Scheduled rule for NOAA polling (every 30 minutes)
- [ ] Scheduled rule for TOU window check (hourly)
- [ ] Dead letter queue for failed events
- [ ] CloudWatch log group for event debugging

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create events module variables**

Create `sunshift/infra/modules/events/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "lambda_hurricane_arn" {
  description = "ARN of Hurricane Shield Lambda function"
  type        = string
  default     = ""
}

variable "lambda_tou_scheduler_arn" {
  description = "ARN of TOU Scheduler Lambda function"
  type        = string
  default     = ""
}

variable "enable_noaa_polling" {
  description = "Enable NOAA alert polling"
  type        = bool
  default     = true
}

variable "noaa_poll_rate" {
  description = "NOAA polling rate expression"
  type        = string
  default     = "rate(30 minutes)"
}

variable "tou_check_rate" {
  description = "TOU schedule check rate expression"
  type        = string
  default     = "rate(1 hour)"
}
```

- [ ] **Step 2: Create events module main.tf**

Create `sunshift/infra/modules/events/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Custom Event Bus
resource "aws_cloudwatch_event_bus" "main" {
  name = "${local.name_prefix}-events"

  tags = {
    Name = "${local.name_prefix}-events"
  }
}

# Dead Letter Queue for failed events
resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name_prefix}-events-dlq"
  message_retention_seconds = 1209600  # 14 days

  tags = {
    Name = "${local.name_prefix}-events-dlq"
  }
}

# SQS Queue Policy for EventBridge
resource "aws_sqs_queue_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.dlq.arn
      }
    ]
  })
}

# CloudWatch Log Group for event debugging
resource "aws_cloudwatch_log_group" "events" {
  name              = "/aws/events/${local.name_prefix}"
  retention_in_days = 7

  tags = {
    Name = "${local.name_prefix}-events-logs"
  }
}

# NOAA Alert Polling Rule
resource "aws_cloudwatch_event_rule" "noaa_polling" {
  count = var.enable_noaa_polling && var.lambda_hurricane_arn != "" ? 1 : 0

  name                = "${local.name_prefix}-noaa-polling"
  description         = "Poll NOAA for hurricane alerts every 30 minutes"
  schedule_expression = var.noaa_poll_rate
  event_bus_name      = "default"  # Scheduled rules must use default bus

  tags = {
    Name = "${local.name_prefix}-noaa-polling"
  }
}

resource "aws_cloudwatch_event_target" "noaa_polling" {
  count = var.enable_noaa_polling && var.lambda_hurricane_arn != "" ? 1 : 0

  rule      = aws_cloudwatch_event_rule.noaa_polling[0].name
  target_id = "HurricaneShield"
  arn       = var.lambda_hurricane_arn

  dead_letter_config {
    arn = aws_sqs_queue.dlq.arn
  }

  retry_policy {
    maximum_event_age_in_seconds = 3600
    maximum_retry_attempts       = 3
  }
}

# TOU Schedule Check Rule
resource "aws_cloudwatch_event_rule" "tou_check" {
  count = var.lambda_tou_scheduler_arn != "" ? 1 : 0

  name                = "${local.name_prefix}-tou-check"
  description         = "Check TOU schedule and trigger migrations"
  schedule_expression = var.tou_check_rate
  event_bus_name      = "default"

  tags = {
    Name = "${local.name_prefix}-tou-check"
  }
}

resource "aws_cloudwatch_event_target" "tou_check" {
  count = var.lambda_tou_scheduler_arn != "" ? 1 : 0

  rule      = aws_cloudwatch_event_rule.tou_check[0].name
  target_id = "TOUScheduler"
  arn       = var.lambda_tou_scheduler_arn

  dead_letter_config {
    arn = aws_sqs_queue.dlq.arn
  }

  retry_policy {
    maximum_event_age_in_seconds = 3600
    maximum_retry_attempts       = 3
  }
}

# Event Pattern Rule for custom events
resource "aws_cloudwatch_event_rule" "custom_events" {
  name           = "${local.name_prefix}-custom-events"
  description    = "Route custom SunShift events"
  event_bus_name = aws_cloudwatch_event_bus.main.name

  event_pattern = jsonencode({
    source      = ["sunshift"]
    detail-type = ["HurricaneAlert", "MigrationComplete", "AgentStatusChange"]
  })

  tags = {
    Name = "${local.name_prefix}-custom-events"
  }
}

# Log all custom events for debugging
resource "aws_cloudwatch_event_target" "log_custom_events" {
  rule           = aws_cloudwatch_event_rule.custom_events.name
  target_id      = "CloudWatchLogs"
  arn            = aws_cloudwatch_log_group.events.arn
  event_bus_name = aws_cloudwatch_event_bus.main.name
}

# Resource policy to allow EventBridge to log to CloudWatch
resource "aws_cloudwatch_log_resource_policy" "events" {
  policy_name = "${local.name_prefix}-events-log-policy"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.events.arn}:*"
      }
    ]
  })
}
```

- [ ] **Step 3: Create events module outputs**

Create `sunshift/infra/modules/events/outputs.tf`:

```hcl
output "event_bus_name" {
  description = "Custom event bus name"
  value       = aws_cloudwatch_event_bus.main.name
}

output "event_bus_arn" {
  description = "Custom event bus ARN"
  value       = aws_cloudwatch_event_bus.main.arn
}

output "dlq_arn" {
  description = "Dead letter queue ARN"
  value       = aws_sqs_queue.dlq.arn
}

output "dlq_url" {
  description = "Dead letter queue URL"
  value       = aws_sqs_queue.dlq.url
}

output "events_log_group_name" {
  description = "CloudWatch log group name for events"
  value       = aws_cloudwatch_log_group.events.name
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/events && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/events/
git commit -m "feat(sp4): events module — EventBridge rules, NOAA polling, TOU scheduler, DLQ"
```

---

### Task 7: Monitoring Module — CloudWatch Dashboards and Alarms

**Goal:** Create CloudWatch dashboard with key metrics and alarms for ECS, Lambda, and DynamoDB.

**Files:**
- Create: `sunshift/infra/modules/monitoring/main.tf`
- Create: `sunshift/infra/modules/monitoring/variables.tf`
- Create: `sunshift/infra/modules/monitoring/outputs.tf`

**Acceptance Criteria:**
- [ ] CloudWatch dashboard with ECS metrics (CPU, Memory)
- [ ] Dashboard panels for Lambda invocations and errors
- [ ] Dashboard panels for DynamoDB throttling
- [ ] Alarm for ECS service unhealthy tasks
- [ ] Alarm for Lambda errors
- [ ] SNS topic for alarm notifications

**Verify:** `terraform validate` passes

**Steps:**

- [ ] **Step 1: Create monitoring module variables**

Create `sunshift/infra/modules/monitoring/variables.tf`:

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "ecs_cluster_name" {
  description = "ECS cluster name for metrics"
  type        = string
}

variable "ecs_service_name" {
  description = "ECS service name for metrics"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for metrics"
  type        = string
}

variable "alarm_email" {
  description = "Email for alarm notifications"
  type        = string
  default     = ""
}

variable "enable_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}
```

- [ ] **Step 2: Create monitoring module main.tf**

Create `sunshift/infra/modules/monitoring/main.tf`:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# SNS Topic for Alarms
resource "aws_sns_topic" "alarms" {
  name = "${local.name_prefix}-alarms"

  tags = {
    Name = "${local.name_prefix}-alarms"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count = var.alarm_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# SunShift ${var.environment} Dashboard"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 12
        height = 6
        properties = {
          title  = "ECS CPU Utilization"
          region = data.aws_region.current.name
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 1
        width  = 12
        height = 6
        properties = {
          title  = "ECS Memory Utilization"
          region = data.aws_region.current.name
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 12
        height = 6
        properties = {
          title  = "DynamoDB Read/Write Capacity"
          region = data.aws_region.current.name
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", var.dynamodb_table_name],
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", var.dynamodb_table_name]
          ]
          period = 300
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 7
        width  = 12
        height = 6
        properties = {
          title  = "DynamoDB Throttled Requests"
          region = data.aws_region.current.name
          metrics = [
            ["AWS/DynamoDB", "ThrottledRequests", "TableName", var.dynamodb_table_name]
          ]
          period = 300
          stat   = "Sum"
        }
      }
    ]
  })
}

data "aws_region" "current" {}

# ECS CPU Alarm
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${local.name_prefix}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization is above 80%"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  ok_actions          = [aws_sns_topic.alarms.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name = "${local.name_prefix}-ecs-cpu-high"
  }
}

# ECS Memory Alarm
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${local.name_prefix}-ecs-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS Memory utilization is above 80%"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  ok_actions          = [aws_sns_topic.alarms.arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name = "${local.name_prefix}-ecs-memory-high"
  }
}

# DynamoDB Throttling Alarm
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttled" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${local.name_prefix}-dynamodb-throttled"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "DynamoDB has throttled requests"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  ok_actions          = [aws_sns_topic.alarms.arn]

  dimensions = {
    TableName = var.dynamodb_table_name
  }

  tags = {
    Name = "${local.name_prefix}-dynamodb-throttled"
  }
}
```

- [ ] **Step 3: Create monitoring module outputs**

Create `sunshift/infra/modules/monitoring/outputs.tf`:

```hcl
output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alarms"
  value       = aws_sns_topic.alarms.arn
}
```

- [ ] **Step 4: Validate module**

```bash
cd sunshift/infra/modules/monitoring && terraform init && terraform validate
```

- [ ] **Step 5: Commit**

```bash
git add sunshift/infra/modules/monitoring/
git commit -m "feat(sp4): monitoring module — CloudWatch dashboard, alarms, SNS notifications"
```

---

### Task 8: Dev Environment — Wire All Modules Together

**Goal:** Create the dev environment main.tf that wires all modules together with proper dependencies and outputs.

**Files:**
- Create: `sunshift/infra/environments/dev/main.tf`
- Create: `sunshift/infra/environments/dev/outputs.tf`

**Acceptance Criteria:**
- [ ] All modules instantiated with correct dependencies
- [ ] Outputs expose ALB DNS, S3 buckets, DynamoDB table
- [ ] `terraform plan` succeeds with no errors
- [ ] Resources follow naming convention

**Verify:** `terraform init && terraform plan` succeeds

**Steps:**

- [ ] **Step 1: Create dev environment main.tf**

Create `sunshift/infra/environments/dev/main.tf`:

```hcl
# Networking
module "networking" {
  source = "../../modules/networking"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  enable_nat_gateway = true
  single_nat_gateway = true  # Cost saving for dev
}

# Storage (needs KMS key from security)
module "storage" {
  source = "../../modules/storage"

  project_name = var.project_name
  environment  = var.environment
  kms_key_arn  = module.security.kms_customer_data_key_arn

  depends_on = [module.security]
}

# Database
module "database" {
  source = "../../modules/database"

  project_name = var.project_name
  environment  = var.environment
}

# Security (needs storage and database for IAM policies)
module "security" {
  source = "../../modules/security"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  vpc_cidr_block     = module.networking.vpc_cidr_block
  s3_bucket_arns     = []  # Will be updated after storage module
  dynamodb_table_arn = ""  # Will be updated after database module

  depends_on = [module.networking]
}

# Update security module with actual ARNs using a second instance
# (This is a workaround for circular dependency)
module "security_updated" {
  source = "../../modules/security"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  vpc_cidr_block     = module.networking.vpc_cidr_block
  s3_bucket_arns     = module.storage.all_bucket_arns
  dynamodb_table_arn = module.database.table_arn

  depends_on = [module.storage, module.database]
}

# ECS
module "ecs" {
  source = "../../modules/ecs"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.networking.vpc_id
  public_subnet_ids       = module.networking.public_subnet_ids
  private_subnet_ids      = module.networking.private_subnet_ids
  alb_security_group_id   = module.security.alb_security_group_id
  ecs_security_group_id   = module.security.ecs_tasks_security_group_id
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  task_role_arn           = module.security.ecs_task_role_arn
  cpu                     = var.ecs_cpu
  memory                  = var.ecs_memory
  desired_count           = var.ecs_desired_count

  environment_variables = {
    SUNSHIFT_DEBUG                 = "true"
    SUNSHIFT_AWS_REGION            = var.aws_region
    SUNSHIFT_S3_BUCKET_CUSTOMER_DATA = module.storage.customer_data_bucket_name
    SUNSHIFT_S3_BUCKET_ML_ARTIFACTS  = module.storage.ml_artifacts_bucket_name
    SUNSHIFT_DYNAMODB_TABLE          = module.database.table_name
  }

  depends_on = [module.security, module.storage, module.database]
}

# Events
module "events" {
  source = "../../modules/events"

  project_name         = var.project_name
  environment          = var.environment
  enable_noaa_polling  = true
  lambda_hurricane_arn = ""  # Will be set when Lambda module is created
}

# Monitoring
module "monitoring" {
  source = "../../modules/monitoring"

  project_name        = var.project_name
  environment         = var.environment
  ecs_cluster_name    = module.ecs.cluster_name
  ecs_service_name    = module.ecs.service_name
  dynamodb_table_name = module.database.table_name
  enable_alarms       = false  # Disable alarms for dev

  depends_on = [module.ecs, module.database]
}
```

- [ ] **Step 2: Create dev environment outputs.tf**

Create `sunshift/infra/environments/dev/outputs.tf`:

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "alb_dns_name" {
  description = "ALB DNS name for API access"
  value       = module.ecs.alb_dns_name
}

output "api_url" {
  description = "API URL"
  value       = "http://${module.ecs.alb_dns_name}"
}

output "s3_customer_data_bucket" {
  description = "S3 bucket for customer data"
  value       = module.storage.customer_data_bucket_name
}

output "s3_ml_artifacts_bucket" {
  description = "S3 bucket for ML artifacts"
  value       = module.storage.ml_artifacts_bucket_name
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = module.database.table_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${module.monitoring.dashboard_name}"
}

output "event_bus_name" {
  description = "EventBridge event bus name"
  value       = module.events.event_bus_name
}
```

- [ ] **Step 3: Initialize and validate**

```bash
cd sunshift/infra/environments/dev
terraform init
terraform validate
terraform plan -out=tfplan
```

Expected: Plan succeeds, shows all resources to be created.

- [ ] **Step 4: Commit**

```bash
git add sunshift/infra/environments/dev/
git commit -m "feat(sp4): dev environment — all modules wired together with outputs"
```

---

### Task 9: GitHub Actions CI/CD Pipeline

**Goal:** Create GitHub Actions workflow for Terraform validation, planning, and deployment with manual approval for production.

**Files:**
- Create: `sunshift/.github/workflows/terraform.yml`

**Acceptance Criteria:**
- [ ] Workflow triggers on push to main and pull requests
- [ ] Validates Terraform syntax
- [ ] Runs `terraform plan` and posts to PR comments
- [ ] Manual approval required for production deploy
- [ ] Secrets managed via GitHub Secrets

**Verify:** Workflow YAML is valid

**Steps:**

- [ ] **Step 1: Create GitHub Actions workflow**

Create `sunshift/.github/workflows/terraform.yml`:

```yaml
name: Terraform

on:
  push:
    branches: [main]
    paths:
      - 'sunshift/infra/**'
  pull_request:
    branches: [main]
    paths:
      - 'sunshift/infra/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - prod

env:
  TF_VERSION: '1.9.0'
  AWS_REGION: 'us-east-2'

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: sunshift/infra/environments/dev

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive ../../

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

  plan-dev:
    name: Plan (Dev)
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'pull_request' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'dev')
    defaults:
      run:
        working-directory: sunshift/infra/environments/dev

    permissions:
      contents: read
      pull-requests: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -no-color -out=tfplan 2>&1 | tee plan_output.txt
          echo "plan<<EOF" >> $GITHUB_OUTPUT
          cat plan_output.txt >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Comment Plan on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const plan = `${{ steps.plan.outputs.plan }}`;
            const truncatedPlan = plan.length > 65000 ? plan.substring(0, 65000) + '\n... (truncated)' : plan;
            const body = `## Terraform Plan (Dev)

            <details>
            <summary>Show Plan</summary>

            \`\`\`hcl
            ${truncatedPlan}
            \`\`\`

            </details>`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Upload Plan Artifact
        uses: actions/upload-artifact@v4
        with:
          name: tfplan-dev
          path: sunshift/infra/environments/dev/tfplan

  deploy-dev:
    name: Deploy (Dev)
    runs-on: ubuntu-latest
    needs: plan-dev
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: dev
    defaults:
      run:
        working-directory: sunshift/infra/environments/dev

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Apply
        run: terraform apply -auto-approve

      - name: Output Summary
        run: |
          echo "## Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Output | Value |" >> $GITHUB_STEP_SUMMARY
          echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
          terraform output -json | jq -r 'to_entries[] | "| \(.key) | \(.value.value) |"' >> $GITHUB_STEP_SUMMARY
```

- [ ] **Step 2: Validate workflow syntax**

```bash
# Install actionlint if not available
# brew install actionlint
cd sunshift && actionlint .github/workflows/terraform.yml || echo "Install actionlint to validate"
```

- [ ] **Step 3: Commit**

```bash
git add sunshift/.github/
git commit -m "feat(sp4): GitHub Actions CI/CD — Terraform validate, plan, deploy with PR comments"
```

---

### Task 10: Deploy Script and Documentation

**Goal:** Create deployment helper script and update project documentation with infrastructure setup instructions.

**Files:**
- Create: `sunshift/infra/scripts/deploy.sh`
- Update: `sunshift/infra/README.md`

**Acceptance Criteria:**
- [ ] `deploy.sh` script handles init, plan, apply workflow
- [ ] README documents all modules and usage
- [ ] Clear instructions for first-time setup
- [ ] Environment variable requirements documented

**Verify:** Scripts are executable, README is complete

**Steps:**

- [ ] **Step 1: Create deploy.sh script**

Create `sunshift/infra/scripts/deploy.sh`:

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"

usage() {
    echo "Usage: $0 <environment> <command>"
    echo ""
    echo "Environments: dev, prod"
    echo "Commands: init, plan, apply, destroy, output"
    echo ""
    echo "Examples:"
    echo "  $0 dev init     # Initialize Terraform for dev"
    echo "  $0 dev plan     # Show planned changes"
    echo "  $0 dev apply    # Apply changes"
    echo "  $0 dev output   # Show outputs"
    exit 1
}

if [[ $# -lt 2 ]]; then
    usage
fi

ENVIRONMENT="$1"
COMMAND="$2"
ENV_DIR="${INFRA_DIR}/environments/${ENVIRONMENT}"

if [[ ! -d "$ENV_DIR" ]]; then
    echo "Error: Environment '$ENVIRONMENT' not found at $ENV_DIR"
    exit 1
fi

cd "$ENV_DIR"

case "$COMMAND" in
    init)
        echo "Initializing Terraform for ${ENVIRONMENT}..."
        terraform init
        ;;
    plan)
        echo "Planning changes for ${ENVIRONMENT}..."
        terraform plan -out=tfplan
        ;;
    apply)
        if [[ -f "tfplan" ]]; then
            echo "Applying saved plan for ${ENVIRONMENT}..."
            terraform apply tfplan
            rm -f tfplan
        else
            echo "Applying changes for ${ENVIRONMENT}..."
            terraform apply
        fi
        ;;
    destroy)
        echo "WARNING: This will destroy all resources in ${ENVIRONMENT}!"
        read -p "Type 'yes' to confirm: " confirm
        if [[ "$confirm" == "yes" ]]; then
            terraform destroy
        else
            echo "Aborted."
            exit 1
        fi
        ;;
    output)
        terraform output
        ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
```

- [ ] **Step 2: Create infrastructure README**

Create `sunshift/infra/README.md`:

```markdown
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
```

- [ ] **Step 3: Make scripts executable**

```bash
chmod +x sunshift/infra/scripts/*.sh
```

- [ ] **Step 4: Commit**

```bash
git add sunshift/infra/scripts/ sunshift/infra/README.md
git commit -m "feat(sp4): deploy script + infrastructure documentation"
```

---

## Verification — End-to-End Checklist

After all tasks complete:

1. `cd sunshift/infra/environments/dev && terraform init` → succeeds
2. `terraform validate` → no errors
3. `terraform plan` → shows all resources to create
4. `terraform apply` → (optional, requires AWS account) deploys infrastructure
5. Modules are reusable across environments
6. CI/CD pipeline validates Terraform on PR
7. Documentation is complete

## Estimated AWS Resources

| Resource | Count | Purpose |
|----------|-------|---------|
| VPC | 1 | Network isolation |
| Subnets | 4 | 2 public, 2 private |
| NAT Gateway | 1 | Private subnet internet access |
| ALB | 1 | Load balancing |
| ECS Cluster | 1 | Container orchestration |
| ECS Service | 1 | FastAPI backend |
| S3 Buckets | 4 | customer-data, ml-artifacts, raw-data, audit-logs |
| DynamoDB Table | 1 | Single-table design |
| KMS Keys | 2 | customer-data, app-secrets |
| EventBridge Rules | 3 | NOAA polling, TOU check, custom events |
| CloudWatch Dashboard | 1 | Observability |
| IAM Roles | 3 | ECS execution, ECS task, Lambda |
