# AWS Deployment Prep

> **Historical architecture only.** The AWS account/backend is retired. Current
> production uses Vercel Functions and Neon PostgreSQL.

This document covers everything you need to do **before** running `sam deploy` in Phase 7.

> **Status:** Phase 6 only prepares files. No AWS resources have been created yet.

---

## Required local tools

### 1. AWS CLI
```bash
# Check if installed
aws --version
# Should output: aws-cli/2.x.x ...

# Install (macOS with Homebrew)
brew install awscli

# Or download the official installer:
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
```

### 2. AWS SAM CLI
```bash
# Check if installed
sam --version
# Should output: SAM CLI, version 1.x.x

# Install (macOS with Homebrew)
brew install aws-sam-cli

# Or download:
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

### 3. Docker Desktop
```bash
docker --version
# Needed for SAM local testing and the existing local dev workflow
```

---

## AWS account safety steps

Do these **before** deploying anything to AWS. They cost nothing and prevent surprise bills.

### Create a $1 billing alert
1. AWS Console → Billing → Budgets → Create a budget
2. Choose **Cost budget** → Monthly → Set amount: `$1.00`
3. Add your email as an alert at 80% and 100% threshold
4. This will alert you if you accidentally spin up something expensive

### Enable Cost Anomaly Detection (free)
1. AWS Console → Billing → Cost Anomaly Detection
2. Create a monitor → Service monitor → All AWS services
3. Set alert threshold: $1.00
4. This catches unexpected usage before it compounds

### Check your Free Tier usage
AWS Console → Billing → Free Tier — review what you've used this month.
Lambda: 1M requests/month free. DynamoDB: 25 GB + 25 RCU/WCU free.

---

## Services used (all free-tier friendly)

| Service | Why | Cost model |
|---|---|---|
| **Lambda** | Runs the FastAPI app (via Mangum) | 1M req/mo free; $0.20/1M after |
| **DynamoDB on-demand** | NoSQL database | 25 GB storage free; $0 until real traffic |
| **API Gateway HTTP API** | Routes requests to Lambda | 1M req/mo free; ~$1/1M after |
| **SAM / CloudFormation** | Deploys the stack | Free |

## Services to AVOID

| Service | Why to avoid |
|---|---|
| **EKS** | $72/mo minimum (control plane) |
| **RDS** | Always-on instance; not needed here |
| **NAT Gateway** | $32/mo minimum; unnecessary if Lambda not in VPC |
| **EC2 (always-on)** | Defeats the serverless cost model |
| **API Gateway REST API** | 3.5× more expensive than HTTP API |
| **Cognito** | Not needed for anonymous MVP |

---

## IAM / credentials setup

### Option A: AWS IAM Identity Center (recommended for new accounts)
1. Enable IAM Identity Center in your AWS account
2. Create a user and assign the `AdministratorAccess` permission set
3. Run `aws configure sso` and follow the prompts
4. Test: `aws sts get-caller-identity`

### Option B: IAM user with access key (simpler but less secure)
1. AWS Console → IAM → Users → Create user
2. Attach policy: `AdministratorAccess` (tighten later)
3. Create access key → download CSV
4. Run: `aws configure`
   - AWS Access Key ID: `<from CSV>`
   - AWS Secret Access Key: `<from CSV>`
   - Default region: `us-east-1`
   - Default output format: `json`
5. Test: `aws sts get-caller-identity`

> **Security tip:** Do not share access keys. Do not commit them. Rotate them after ~90 days.

---

## Environment variables for deployment

### Backend Lambda (set via SAM `parameter_overrides` in `samconfig.toml`)

| Variable | Value | Notes |
|---|---|---|
| `AWS_REGION` | `us-east-1` | Or your preferred region |
| `DYNAMODB_TABLE_NAME` | `matcha_scout` | Must match table created by SAM |
| `USE_MOCK_AI` | `false` | Use real Gemini in prod |
| `GEMINI_API_KEY` | `your_key` | Get free key at aistudio.google.com |

> `DYNAMODB_ENDPOINT_URL` is **not set** in Lambda — boto3 uses the real AWS DynamoDB endpoint automatically.

### Frontend (set in Vercel or `.env.local`)

| Variable | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod` | From SAM `Outputs.ApiUrl` after deploy |

---

## What's already prepared (Phase 6)

- ✅ Lambda handler: `backend/app/lambda_handler.py`
- ✅ Mangum added to `backend/requirements.txt`
- ✅ `backend/app/core/config.py` — safe for both local and Lambda modes
- ✅ `backend/app/services/db.py` — omits local-only endpoint when unset
- ✅ `infra/aws/template.yaml` — SAM CloudFormation template
- ✅ `infra/aws/samconfig.example.toml` — example config (copy → fill → `samconfig.toml`)

## What Phase 7 will do

See [`phase-7-deployment-runbook.md`](phase-7-deployment-runbook.md) for the full step-by-step.

---

## Commands NOT to run yet

```bash
# ❌ DO NOT RUN DURING PHASE 6 ❌
sam build
sam deploy --guided
aws dynamodb create-table ...
aws cloudformation deploy ...
```

These are Phase 7 commands. Running them now will create real AWS resources and may incur cost.
