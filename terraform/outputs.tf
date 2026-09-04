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