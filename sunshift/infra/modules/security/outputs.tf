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
