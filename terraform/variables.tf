variable "aws_region" {
  description = "AWS region where regional project resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base name used for project resources"
  type        = string
  default     = "serverless-three-tier"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}