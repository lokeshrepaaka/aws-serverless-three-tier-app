# --------------------------------------------------
# Amazon Cognito User Pool
# --------------------------------------------------

resource "aws_cognito_user_pool" "users" {
  name = "${var.project_name}-${var.environment}-users"

  username_attributes = ["email"]

  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-users"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# --------------------------------------------------
# Cognito App Client
# --------------------------------------------------

resource "aws_cognito_user_pool_client" "frontend" {
  name = "${var.project_name}-${var.environment}-frontend"

  user_pool_id = aws_cognito_user_pool.users.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}