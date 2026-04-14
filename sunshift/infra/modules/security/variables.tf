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
