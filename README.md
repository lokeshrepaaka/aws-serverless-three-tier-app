AWS Serverless Three-Tier Task Tracker

A production-style serverless web application built on AWS using Terraform, GitHub Actions, Cognito authentication, and a fully serverless three-tier architecture.

The application lets users create accounts, verify their email, sign in securely, and manage private tasks. Each user's tasks are isolated using the Cognito JWT sub claim and enforced in the Lambda/DynamoDB application layer.

Live Application

Frontend: https://d3ql7kg50manzy.cloudfront.net

This project is intended as a Cloud/DevOps portfolio project and may be taken offline when not actively demonstrated to avoid unnecessary AWS costs.

Architecture

flowchart TB
    U[User Browser]

    subgraph Presentation["Presentation Tier"]
        CF[Amazon CloudFront]
        S3[Private Amazon S3 Frontend Bucket]
    end

    subgraph Identity["Authentication & Authorization"]
        COG[Amazon Cognito User Pool]
        AUTH[API Gateway JWT Authorizer]
    end

    subgraph Application["Application Tier"]
        API[Amazon API Gateway HTTP API]
        LAMBDA[AWS Lambda<br/>Python]
    end

    subgraph Data["Data Tier"]
        DDB[Amazon DynamoDB<br/>Tasks Table]
    end

    subgraph Observability["Observability"]
        CWL[Amazon CloudWatch Logs]
        CWA[CloudWatch Alarms]
    end

    subgraph DevOps["Infrastructure & CI/CD"]
        GH[GitHub]
        GHA[GitHub Actions]
        OIDC[GitHub OIDC → AWS IAM]
        TF[Terraform]
        STATE[Private S3 Terraform Backend<br/>Versioning + State Locking]
    end

    U -->|HTTPS| CF
    CF --> S3
    U -->|Sign up / Sign in| COG
    U -->|Bearer JWT| API
    API --> AUTH
    AUTH -->|Validated request| LAMBDA
    LAMBDA --> DDB
    LAMBDA --> CWL
    API --> CWL
    LAMBDA --> CWA

    GH --> GHA
    GHA --> OIDC
    OIDC --> TF
    TF --> Presentation
    TF --> Identity
    TF --> Application
    TF --> Data
    TF --> Observability
    TF <--> STATE

Request Flow

The browser loads the frontend through Amazon CloudFront.

CloudFront serves the application from a private S3 origin.

Users register and authenticate with Amazon Cognito.

The frontend sends the Cognito access token in the Authorization header.

API Gateway validates the JWT before forwarding the request.

Lambda extracts the verified Cognito sub claim and uses it as the task owner ID.

DynamoDB stores task data, and Lambda restricts reads and mutations to the authenticated owner.

AWS Services

Service

Purpose

Amazon S3

Hosts the private frontend and stores Terraform remote state

Amazon CloudFront

Secure CDN and public entry point for the frontend

Amazon Cognito

User registration, email verification, and authentication

Amazon API Gateway

HTTP API and JWT authorization

AWS Lambda

Python application logic for task CRUD operations

Amazon DynamoDB

Serverless task storage

AWS IAM

Runtime permissions, Terraform deployment permissions, and GitHub OIDC role

Amazon CloudWatch

Application/API logs and operational alarms

Features

User self-registration

Email verification with Cognito

Secure sign-in and sign-out

JWT-protected API routes

Create, read, complete, and delete tasks

Per-user task isolation

Responsive frontend

Private S3 frontend origin

CloudFront distribution

Restricted API CORS

CloudWatch logging

Lambda error and throttle alarms

Terraform-managed AWS infrastructure

S3 remote Terraform state

Native Terraform state locking

GitHub Actions CI/CD

Secretless GitHub-to-AWS authentication using OIDC

Controlled Terraform apply through manual workflow dispatch

Security Design

Cognito Authentication

The frontend uses an Amazon Cognito User Pool. Users create an account with an email address, verify the account using an emailed confirmation code, and then authenticate before using the task API.

The browser application uses a Cognito App Client without a client secret because a browser cannot securely protect a static secret.

JWT Authorization

All task routes are protected by an API Gateway JWT authorizer.

Protected routes:

GET    /tasks
POST   /tasks
PATCH  /tasks/{task_id}
DELETE /tasks/{task_id}

Requests must contain a valid Cognito access token.

Per-User Data Isolation

Authentication alone is not enough for a multi-user application. Lambda extracts the verified Cognito sub claim from API Gateway's JWT context and stores it as owner_id on each task.

The backend then enforces ownership on all task operations:

Authenticated Cognito user
          │
          ▼
      JWT "sub"
          │
          ▼
       owner_id
          │
          ▼
     DynamoDB task

This prevents one authenticated user from reading, updating, or deleting another user's tasks.

IAM Separation

The project separates deployment permissions from application runtime permissions.

Lambda execution role: only the permissions required by the running application.

GitHub Actions role: temporary deployment credentials assumed through OIDC.

Local Terraform identity: used during local infrastructure development.

No long-lived AWS access keys are stored in GitHub.

Infrastructure as Code

All AWS infrastructure is managed using Terraform.

Terraform manages resources including:

S3 frontend infrastructure

CloudFront distribution

DynamoDB table

Lambda function and execution role

API Gateway HTTP API

Cognito User Pool and App Client

CloudWatch log groups

CloudWatch alarms

The AWS provider and Archive provider are version-constrained in Terraform.

Remote Terraform State

Terraform state is stored remotely in a private S3 bucket:

serverless-three-tier-terraform-state-585008089387

State key:

serverless-three-tier/dev/terraform.tfstate

The backend uses:

S3 server-side encryption

S3 versioning

Terraform native S3 lock files

Remote state prevents the project from depending on one developer workstation and allows CI/CD and local Terraform to work against the same state safely.

CI/CD Pipeline

GitHub Actions authenticates to AWS using OpenID Connect instead of stored AWS access keys.

GitHub Push / Manual Run
          │
          ▼
    GitHub Actions
          │
          ▼
     GitHub OIDC
          │
          ▼
       AWS IAM
          │
          ▼
       Terraform

On Push to main

The workflow runs:

terraform fmt -check
terraform init
terraform validate
terraform plan

A normal push performs validation and planning but does not automatically apply infrastructure changes.

Manual Deployment

A manually triggered workflow_dispatch run performs the same checks and then executes:

terraform apply -auto-approve tfplan

The saved Terraform plan is applied so the deployment uses the exact infrastructure changes that were reviewed during the workflow.

Repository Structure

aws-serverless-three-tier-app/
│
├── .github/
│   ├── iam/
│   │   ├── github-actions-deployment-policy.json
│   │   └── github-actions-trust-policy.json
│   └── workflows/
│       └── deploy.yml
│
├── backend/
│   └── lambda_function.py
│
├── diagrams/
│
├── frontend/
│   └── index.html
│
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
│
├── .gitattributes
├── .gitignore
└── README.md

Local Terraform Workflow

Set the AWS CLI profile for the PowerShell session:

$env:AWS_PROFILE="serverless-dev"

Run Terraform from the terraform directory:

cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan

Infrastructure changes can then be reviewed before applying:

terraform apply

Frontend Deployment

The frontend is uploaded to the private S3 bucket and served through CloudFront.

Example deployment:

aws s3 cp frontend/index.html `
  s3://serverless-three-tier-dev-frontend-1cc456121e173a894d36b910ea/index.html `
  --content-type "text/html" `
  --profile serverless-dev

Invalidate the CloudFront cache after updating the frontend:

aws cloudfront create-invalidation `
  --distribution-id E22ODV22PZU871 `
  --paths "/*" `
  --profile serverless-dev

Testing

The application was tested across the complete authentication and task flow:

Account creation

Email verification

Sign-in

JWT-protected API access

Create task

Read tasks

Complete task

Delete task

Sign-out

Unauthorized requests rejected

Two separate Cognito accounts tested

User A cannot see User B's tasks

User B cannot see User A's tasks

Terraform remote state locking verified

GitHub Actions OIDC authentication verified

Local and CI-generated Lambda packages normalized for consistent Terraform hashes

Final Terraform plan verified with no infrastructure drift

Observability

The project includes explicit CloudWatch log groups for:

Lambda application logs

API Gateway access logs

CloudWatch alarms monitor:

Lambda errors

Lambda throttling

Log retention is managed through Terraform.

Engineering Challenges Solved

Cross-Platform Lambda Packaging

Terraform packages the Lambda source using the Archive provider. Windows CRLF line endings originally produced a different ZIP checksum from the Linux-based GitHub Actions runner.

The repository now enforces LF line endings with .gitattributes, and the repository-local Git configuration avoids automatic CRLF conversion. This keeps Lambda package hashes consistent between local development and CI/CD.

Terraform State Concurrency

Remote Terraform state uses S3 native lock files. When GitHub Actions held the state lock during a plan, a simultaneous local Terraform operation was correctly blocked rather than allowing concurrent state operations.

Cognito Partial Apply Recovery

During Cognito provisioning, a resource was created before Terraform encountered an IAM read-permission failure. The resource state and taint status were inspected before continuing rather than blindly recreating the user pool.

GitHub OIDC Subject Format

The repository uses GitHub's immutable OIDC subject format for newly created repositories, allowing the AWS IAM trust policy to restrict role assumption to this specific repository and branch.

Design Decisions

Why serverless?
The application does not require always-on servers. API Gateway, Lambda, DynamoDB, Cognito, S3, and CloudFront provide a scalable architecture with minimal infrastructure administration.

Why Terraform?
Infrastructure is repeatable, reviewable, version-controlled, and deployable through CI/CD.

Why OIDC for GitHub Actions?
OIDC eliminates the need to store long-lived AWS credentials as GitHub secrets.

Why controlled apply instead of applying every push?
A push can automatically validate and preview infrastructure changes while production-changing Terraform apply remains an intentional action.

Why Cognito sub for ownership?
The sub claim is an immutable identity generated by Cognito and is safer for authorization than trusting an owner ID supplied by the browser.

Potential Future Improvements

Replace the filtered DynamoDB scan with an access pattern optimized around user ownership

Add API-level 5XX monitoring

Add GitHub Environment approval before Terraform apply

Tighten remaining deployment IAM permissions further

Add automated backend/frontend tests

Add a custom domain and HTTPS certificate

Move the frontend build/deployment into the CI/CD workflow

Use Cognito managed login with OAuth 2.0 Authorization Code + PKCE

What This Project Demonstrates

This project demonstrates practical experience with:

AWS: S3, CloudFront, Lambda, API Gateway, DynamoDB, Cognito, IAM, CloudWatch
Infrastructure as Code: Terraform
CI/CD: GitHub Actions
Cloud Security: IAM, JWT authorization, Cognito, OIDC, CORS, private S3 origins
DevOps: remote state, state locking, deterministic deployments, Git workflows, infrastructure validation
Backend: Python, serverless APIs, DynamoDB CRUD
Frontend: HTML, CSS, JavaScript, REST API integration

Author

Lokesh Repaka

Computer Science student focused on Cloud Engineering and DevOps.