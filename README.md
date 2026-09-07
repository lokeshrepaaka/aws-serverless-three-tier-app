AWS Serverless Three-Tier Task Tracker

Short 2–3 sentence description

[Live Demo]   [Architecture]

────────────────────────────

Architecture
[Your architecture PNG]

────────────────────────────

Key Features
✓ Cognito authentication + email verification
✓ JWT-protected API
✓ Per-user task isolation
✓ Serverless CRUD
✓ Terraform IaC
✓ GitHub Actions + OIDC
✓ Remote state + locking
✓ CloudWatch monitoring

────────────────────────────

Tech Stack
AWS | Terraform | Python | JavaScript | GitHub Actions

────────────────────────────

How It Works
1. CloudFront serves frontend from private S3
2. Cognito authenticates user
3. API Gateway validates JWT
4. Lambda handles CRUD
5. DynamoDB stores user-owned tasks

────────────────────────────

Security & DevOps
Authentication
Authorization
OIDC
IAM
Remote state
Controlled deployments

────────────────────────────

CI/CD
Push → fmt → validate → plan
Manual → plan → apply

────────────────────────────

Project Structure
(short tree)

────────────────────────────

Challenges Solved
• Windows/Linux Lambda hash drift
• Terraform state locking
• Cognito partial apply
• GitHub OIDC trust configuration

────────────────────────────

Future Improvements
(short list)

────────────────────────────

Author
Lokesh Repaka
