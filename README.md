☁️ AWS Serverless Three-Tier Task Tracker

A secure, multi-user task management application built with a serverless three-tier architecture on AWS. The project demonstrates Cloud/DevOps practices including Terraform Infrastructure as Code, GitHub Actions CI/CD, OIDC authentication, Cognito JWT authorization, remote state locking, and CloudWatch observability.

🌐 Live Application · 🏗️ Architecture · ⚙️ CI/CD

Portfolio project: The live AWS environment may occasionally be unavailable when not being demonstrated to avoid unnecessary cloud costs.

🏗️ Architecture



Request Flow

CloudFront serves the frontend from a private S3 bucket.

Amazon Cognito handles registration, email verification, and authentication.

The browser sends the Cognito JWT to API Gateway.

API Gateway validates the JWT before invoking Lambda.

Lambda performs task CRUD operations against DynamoDB.

The Cognito sub is stored as owner_id, keeping each user's tasks isolated.

✨ Key Features

🔐 Cognito signup, email verification, login, and JWT authentication

👥 Per-user task isolation enforced in the backend

⚡ Serverless task CRUD API with API Gateway + Lambda

🌐 Private S3 frontend delivered globally through CloudFront

🏗️ AWS infrastructure managed with Terraform

🚀 GitHub Actions CI/CD with secretless AWS OIDC authentication

🔒 Remote Terraform state with S3 native state locking

📊 CloudWatch logs, error alarms, and throttle alarms

🛡️ Restricted CORS and separated deployment/runtime IAM permissions

🧰 Tech Stack

Area

Technologies

☁️ Cloud

AWS

🎨 Frontend

HTML, CSS, JavaScript

⚙️ Backend

Python, AWS Lambda

🔗 API

Amazon API Gateway HTTP API

🗄️ Database

Amazon DynamoDB

🔐 Authentication

Amazon Cognito + JWT

🏗️ Infrastructure

Terraform

🚀 CI/CD

GitHub Actions + AWS OIDC

📊 Monitoring

Amazon CloudWatch

🔐 Security & Multi-User Authorization

Authentication is handled by Amazon Cognito, while API Gateway protects every task route with a JWT authorizer.

Lambda does not trust an owner ID supplied by the browser. Instead, it reads the verified Cognito sub claim and stores it as owner_id on each task. GET, PATCH, and DELETE operations enforce that ownership so authenticated users cannot access another user's tasks.

Cognito User → JWT → API Gateway → Lambda → owner_id → DynamoDB

Additional security controls include a private S3 frontend origin, CloudFront Origin Access Control, restricted API CORS, IAM role separation, and no long-lived AWS credentials stored in GitHub.

⚙️ CI/CD Pipeline

GitHub Actions authenticates to AWS through OpenID Connect (OIDC) and assumes a dedicated IAM role using temporary credentials.

Push to main
   ↓
fmt → init → validate → plan
   ↓
No automatic apply

Manual workflow_dispatch
   ↓
plan → controlled apply

This keeps infrastructure changes reviewable while still providing an automated deployment workflow.

🏗️ Infrastructure as Code

Terraform provisions and manages the application's AWS infrastructure, including:

S3 · CloudFront · Cognito · API Gateway · Lambda · DynamoDB · IAM · CloudWatch

Terraform state is stored in a private, encrypted, versioned S3 backend with native S3 state locking. Local Terraform and GitHub Actions therefore work against the same protected state.

📁 Project Structure

aws-serverless-three-tier-app/
├── .github/
│   ├── iam/
│   └── workflows/
│       └── deploy.yml
├── backend/
│   └── lambda_function.py
├── diagrams/
│   └── aws-serverless-three-tier-architecture.png
├── frontend/
│   └── index.html
├── terraform/
│   ├── alarms.tf
│   ├── apigateway.tf
│   ├── backend.tf
│   ├── cloudfront.tf
│   ├── cloudwatch.tf
│   ├── cognito.tf
│   ├── dynamodb.tf
│   ├── iam.tf
│   ├── lambda.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── s3.tf
│   └── variables.tf
├── .gitattributes
├── .gitignore
└── README.md

🧪 Validation

The application has been tested for:

Account creation, email verification, login, and logout

Authenticated task create/read/complete/delete operations

Rejection of unauthenticated API requests

Two-user data isolation with separate Cognito accounts

GitHub Actions OIDC authentication to AWS

Terraform remote-state locking

Consistent Lambda packaging between Windows and GitHub Actions/Linux

Zero-drift Terraform planning (No changes)

🧩 Engineering Challenges Solved

Cross-platform Lambda packaging — Windows CRLF line endings initially produced a different Lambda ZIP checksum from GitHub's Linux runner. LF normalization and .gitattributes made packaging deterministic.

Terraform state concurrency — S3 native state locking correctly prevents simultaneous local and CI Terraform operations from modifying the same state.

Cognito provisioning recovery — A partial Terraform apply was diagnosed through state/taint inspection instead of unnecessarily recreating the user pool.

GitHub OIDC trust — The IAM trust policy uses GitHub's repository-specific immutable OIDC subject so AWS deployments do not require stored access keys.

🔭 Future Improvements

Optimize DynamoDB access around user ownership instead of a filtered scan

Add API-level 5XX monitoring

Add GitHub Environment approval before Terraform apply

Add automated application tests

Add a custom domain

Automate frontend deployment through CI/CD

👤 Author

Lokesh Repaka
Computer Science student focused on Cloud Engineering and DevOps.
