data "archive_file" "lambda_package" {
  type = "zip"

  source_file = "${path.module}/../backend/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "tasks" {
  function_name = "${var.project_name}-${var.environment}-tasks"
  description   = "Handles task CRUD operations for the serverless three-tier application"

  role    = aws_iam_role.lambda_execution.arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.lambda_package.output_path
  source_code_hash = data.archive_file.lambda_package.output_base64sha256

  timeout     = 10
  memory_size = 128

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-tasks"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  depends_on = [
    aws_iam_role_policy.lambda_permissions
  ]
}