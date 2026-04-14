locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

resource "aws_cloudwatch_event_bus" "main" {
  name = "${local.name_prefix}-events"

  tags = {
    Name = "${local.name_prefix}-events"
  }
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name_prefix}-events-dlq"
  message_retention_seconds = 1209600

  tags = {
    Name = "${local.name_prefix}-events-dlq"
  }
}

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

resource "aws_cloudwatch_log_group" "events" {
  name              = "/aws/events/${local.name_prefix}"
  retention_in_days = 7

  tags = {
    Name = "${local.name_prefix}-events-logs"
  }
}

resource "aws_cloudwatch_event_rule" "noaa_polling" {
  count = var.enable_noaa_polling && var.lambda_hurricane_arn != "" ? 1 : 0

  name                = "${local.name_prefix}-noaa-polling"
  description         = "Poll NOAA for hurricane alerts every 30 minutes"
  schedule_expression = var.noaa_poll_rate
  event_bus_name      = "default"

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

resource "aws_cloudwatch_event_target" "log_custom_events" {
  rule           = aws_cloudwatch_event_rule.custom_events.name
  target_id      = "CloudWatchLogs"
  arn            = aws_cloudwatch_log_group.events.arn
  event_bus_name = aws_cloudwatch_event_bus.main.name
}

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
