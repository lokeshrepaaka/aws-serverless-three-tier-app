terraform {
  backend "s3" {
    bucket       = "serverless-three-tier-terraform-state-585008089387"
    key          = "serverless-three-tier/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}