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
