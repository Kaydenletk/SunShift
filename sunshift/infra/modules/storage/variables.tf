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
