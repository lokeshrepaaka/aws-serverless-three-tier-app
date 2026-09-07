output "frontend_bucket_name" {
  description = "Name of the S3 bucket storing frontend assets"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_bucket_arn" {
  description = "ARN of the frontend S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name for the frontend"
  value       = aws_cloudfront_distribution.frontend.domain_name
}
output "dynamodb_table_name" {
  description = "Name of the DynamoDB table storing application tasks"
  value       = aws_dynamodb_table.tasks.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table storing application tasks"
  value       = aws_dynamodb_table.tasks.arn
}
output "lambda_execution_role_arn" {
  description = "ARN of the IAM role used by the Lambda function"
  value       = aws_iam_role.lambda_execution.arn
}

output "api_endpoint" {
  description = "Base URL of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.tasks.api_endpoint
}
output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.users.id
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito frontend app client"
  value       = aws_cognito_user_pool_client.frontend.id
}