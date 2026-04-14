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
