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
