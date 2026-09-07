# --------------------------------------------------
# CloudWatch Alarm - Lambda Errors
# --------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name = "${var.project_name}-${var.environment}-lambda-errors"

  alarm_description = "Triggers when the Lambda function records one or more errors."

  namespace   = "AWS/Lambda"
  metric_name = "Errors"

  dimensions = {
    FunctionName = aws_lambda_function.tasks.function_name
  }

  statistic = "Sum"

  period = 300

  evaluation_periods = 1

  threshold = 1

  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-errors"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
# --------------------------------------------------
# CloudWatch Alarm - Lambda Throttles
# --------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name = "${var.project_name}-${var.environment}-lambda-throttles"

  alarm_description = "Triggers when the Lambda function records one or more throttled invocations."

  namespace   = "AWS/Lambda"
  metric_name = "Throttles"

  dimensions = {
    FunctionName = aws_lambda_function.tasks.function_name
  }

  statistic = "Sum"

  period = 300

  evaluation_periods = 1

  threshold = 1

  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-throttles"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}