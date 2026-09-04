data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-${var.environment}-lambda-role"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-role"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid    = "AllowTaskTableAccess"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan"
    ]

    resources = [
      aws_dynamodb_table.tasks.arn
    ]
  }

  statement {
    sid    = "AllowCloudWatchLogging"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-${var.environment}-tasks:*"
    ]
  }
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name = "${var.project_name}-${var.environment}-lambda-permissions"
  role = aws_iam_role.lambda_execution.id

  policy = data.aws_iam_policy_document.lambda_permissions.json
}