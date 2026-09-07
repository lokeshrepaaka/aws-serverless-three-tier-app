# --------------------------------------------------
# CloudWatch Log Group for Lambda
# --------------------------------------------------

resource "aws_cloudwatch_log_group" "lambda_tasks" {
  name = "/aws/lambda/${aws_lambda_function.tasks.function_name}"

  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-logs"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# --------------------------------------------------
# CloudWatch Log Group for API Gateway Access Logs
# --------------------------------------------------

resource "aws_cloudwatch_log_group" "api_access" {
  name = "/aws/apigateway/${var.project_name}-${var.environment}-api"

  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-access-logs"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}