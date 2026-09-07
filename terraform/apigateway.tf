# --------------------------------------------------
# API Gateway HTTP API
# --------------------------------------------------

resource "aws_apigatewayv2_api" "tasks" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://${aws_cloudfront_distribution.frontend.domain_name}"]

    allow_methods = [
      "GET",
      "POST",
      "PATCH",
      "DELETE",
      "OPTIONS"
    ]

    allow_headers = [
      "Content-Type"
    ]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-api"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# --------------------------------------------------
# Lambda integration
# --------------------------------------------------

resource "aws_apigatewayv2_integration" "tasks" {
  api_id = aws_apigatewayv2_api.tasks.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.tasks.invoke_arn
  payload_format_version = "2.0"
}


# --------------------------------------------------
# GET /tasks
# --------------------------------------------------

resource "aws_apigatewayv2_route" "get_tasks" {
  api_id = aws_apigatewayv2_api.tasks.id

  route_key = "GET /tasks"
  target    = "integrations/${aws_apigatewayv2_integration.tasks.id}"
}


# --------------------------------------------------
# POST /tasks
# --------------------------------------------------

resource "aws_apigatewayv2_route" "post_tasks" {
  api_id = aws_apigatewayv2_api.tasks.id

  route_key = "POST /tasks"
  target    = "integrations/${aws_apigatewayv2_integration.tasks.id}"
}


# --------------------------------------------------
# Default stage
# --------------------------------------------------

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.tasks.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_access.arn

    format = jsonencode({
      requestId        = "$context.requestId"
      requestTime      = "$context.requestTime"
      httpMethod       = "$context.httpMethod"
      routeKey         = "$context.routeKey"
      status           = "$context.status"
      responseLength   = "$context.responseLength"
      integrationError = "$context.integrationErrorMessage"
    })
  }
}


# --------------------------------------------------
# Allow API Gateway to invoke Lambda
# --------------------------------------------------

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tasks.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.tasks.execution_arn}/*/*"
}

# --------------------------------------------------
# PATCH /tasks/{task_id}
# --------------------------------------------------

resource "aws_apigatewayv2_route" "patch_task" {
  api_id = aws_apigatewayv2_api.tasks.id

  route_key = "PATCH /tasks/{task_id}"
  target    = "integrations/${aws_apigatewayv2_integration.tasks.id}"
}


# --------------------------------------------------
# DELETE /tasks/{task_id}
# --------------------------------------------------

resource "aws_apigatewayv2_route" "delete_task" {
  api_id = aws_apigatewayv2_api.tasks.id

  route_key = "DELETE /tasks/{task_id}"
  target    = "integrations/${aws_apigatewayv2_integration.tasks.id}"
}