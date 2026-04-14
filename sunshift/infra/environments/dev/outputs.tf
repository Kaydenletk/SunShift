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
