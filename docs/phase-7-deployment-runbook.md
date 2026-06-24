# Phase 7 — Deployment Runbook

> **Historical architecture only.** This records the retired AWS Lambda/API Gateway/DynamoDB deployment. Current production is Next.js and FastAPI on Vercel with Neon PostgreSQL. Do not use this runbook for current releases.

## Deployment record

| | |
|---|---|
| **Stack name** | `matcha-scout-api` |
| **Region** | `us-west-2` |
| **API Gateway URL** | `https://2bd8jfknuc.execute-api.us-west-2.amazonaws.com` |
| **DynamoDB table** | `matcha_scout_prod` |
| **Lambda function** | `matcha-scout-api-prod` |
| **Architecture** | arm64 (Graviton2) |
| **AI mode** | `USE_MOCK_AI=true` (mock parser) |
| **Seeded** | Yes — 5 cafes, 10 drinks, 10 taste profiles |

## Smoke test results (all passed)

```
GET  /health          → {"status":"ok","service":"matcha-scout-api"}
GET  /cafes           → 5 cafes
GET  /drinks          → 10 drinks
GET  /drinks/drink-001/taste-profile → taste profile object
GET  /recommendations → ranked results
POST /reviews         → review saved with mock-parsed taste fields
```

## Bugs fixed during deployment

1. **SAM artifact caching** — `--force-upload` + direct `aws lambda update-function-code` required because SAM reused old S3 artifact even after a clean rebuild
2. **`ReservedConcurrentExecutions: 10` rejected** — new AWS accounts have a 10-concurrency limit leaving no room for a reservation; removed from template
3. **API Gateway stage prefix** — HTTP API v2 with named stage `prod` passes `/prod/path` as `rawPath` to Lambda; fixed by switching to `$default` stage (no prefix in paths)
4. **`UnrecognizedClientException`** — Lambda sets `AWS_SESSION_TOKEN` alongside `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`; passing only partial temp credentials to boto3 fails auth; fixed by only passing explicit credentials in local mode (when `DYNAMODB_ENDPOINT_URL` is set)

## Phase 8 — Connect frontend

The next phase is to connect the deployed frontend to the live backend.

Set `NEXT_PUBLIC_API_BASE_URL` in the frontend (Vercel environment variables or `.env.local`):

```
NEXT_PUBLIC_API_BASE_URL=https://2bd8jfknuc.execute-api.us-west-2.amazonaws.com
```

Then deploy the frontend to Vercel and add the Vercel URL to the CORS whitelist in `infra/aws/template.yaml`.

---

## Original planning commands (for reference)

---

## Pre-flight checklist

Before starting, confirm:

- [ ] AWS CLI is configured: `aws sts get-caller-identity` returns your account ID
- [ ] SAM CLI is installed: `sam --version`
- [ ] Docker Desktop is running: `docker --version`
- [ ] $1 AWS Budget alert is active (see `docs/aws-deployment-prep.md`)
- [ ] You have a Gemini API key from `aistudio.google.com`
- [ ] Local backend passes all tests: `docker compose exec api pytest tests/ -v`
- [ ] Local frontend builds: `cd frontend && npm run build`

---

## Step 1 — Create `samconfig.toml`

```bash
cp infra/aws/samconfig.example.toml infra/aws/samconfig.toml
# Edit samconfig.toml and fill in:
#   - s3_bucket: a unique S3 bucket name (SAM uploads Lambda code here)
#   - region: us-east-1 (or your preferred region)
#   - GeminiApiKey: your real key
```

`samconfig.toml` is gitignored — it will never be committed.

---

## Step 2 — Build the Lambda package

> ⚠️ CREATES NO AWS RESOURCES — safe to run

```bash
cd infra/aws
sam build --template template.yaml
```

What this does:
- Creates a `.aws-sam/build/` directory with the packaged Lambda code
- Installs Python dependencies from `backend/requirements.txt` for the Lambda runtime
- Does **not** touch AWS

Expected output: `Build Succeeded`

If you see a Python version mismatch, add `--use-container` to build inside a Docker container that matches the Lambda runtime.

---

## Step 3 — (First time only) Create an S3 bucket for SAM artifacts

> ⚠️ CREATES AN AWS S3 BUCKET — minimal cost (standard S3 storage rates)

```bash
# Replace YOUR_BUCKET_NAME with something globally unique, e.g. matcha-scout-sam-YOUR_ACCOUNT_ID
aws s3 mb s3://YOUR_BUCKET_NAME --region us-east-1
```

Then update `infra/aws/samconfig.toml` → `s3_bucket = "YOUR_BUCKET_NAME"`

---

## Step 4 — Deploy the stack

> ⚠️ CREATES REAL AWS RESOURCES (Lambda, DynamoDB, API Gateway)

```bash
cd infra/aws
sam deploy --config-file samconfig.toml
```

SAM will show a changeset preview. Review it carefully, then confirm.

What gets created:
1. CloudFormation stack `matcha-scout-prod`
2. DynamoDB table `matcha_scout` (on-demand, single-table design)
3. Lambda function `matcha-scout-api-prod`
4. API Gateway HTTP API

Expected deploy time: ~2–3 minutes

---

## Step 5 — Note the API URL

After deploy, SAM prints the stack outputs:

```
Outputs
-------
Key    ApiUrl
Value  https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod

Key    TableName
Value  matcha_scout
```

Save the `ApiUrl` — you'll need it for the frontend.

---

## Step 6 — Smoke test the API

```bash
API_URL="https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod"

curl "$API_URL/health"
# Expected: {"status":"ok","service":"matcha-scout-api"}

curl "$API_URL/cafes"
# Expected: [] (empty — table exists but not seeded yet)

curl "$API_URL/drinks"
# Expected: []
```

---

## Step 7 — Seed production DynamoDB

> ⚠️ This writes to your real production DynamoDB table.
> Only run once. Verify the table is empty first.

```bash
# Check the table is empty first
aws dynamodb scan \
  --table-name matcha_scout \
  --select COUNT \
  --region us-east-1

# If count is 0, safe to seed:
# Option A: Run seed from inside Docker (points to real DynamoDB, not local)
DYNAMODB_TABLE_NAME=matcha_scout \
AWS_REGION=us-east-1 \
docker compose exec api python -m app.seed.create_tables

DYNAMODB_TABLE_NAME=matcha_scout \
AWS_REGION=us-east-1 \
docker compose exec api python -m app.seed.seed_data

# Note: DYNAMODB_ENDPOINT_URL must NOT be set for this to reach real AWS.
# You may need to run the seed scripts outside Docker with your AWS credentials.
```

> **Safety note:** The seed scripts use `put_item` which is idempotent for
> existing records (they overwrite). Running seed twice is safe for the initial
> fiction data. Do not run seed if real user reviews already exist — it will
> overwrite taste profiles.

---

## Step 8 — Verify seeded data through the API

```bash
curl "$API_URL/cafes"
# Expected: array of 5 cafes

curl "$API_URL/drinks"
# Expected: array of 10 drinks

curl "$API_URL/drinks/drink-001/taste-profile"
# Expected: taste profile object with matcha_strength, etc.

curl "$API_URL/recommendations?matcha_strength=4&sweetness=2&creaminess=3&earthiness=4&bitterness=3"
# Expected: ranked recommendations array
```

---

## Step 9 — Update the frontend

In `frontend/.env.local` (local) or your Vercel environment variables (production):

```
NEXT_PUBLIC_API_BASE_URL=https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod
```

Then rebuild/redeploy the frontend:

```bash
cd frontend && npm run build
```

Or redeploy to Vercel via `git push` if connected.

---

## Step 10 — End-to-end browser test

Run through the [`docs/local-qa-checklist.md`](local-qa-checklist.md) steps, but against the production URL.

Key checks:
- [ ] Landing page loads
- [ ] `/drinks` shows all 10 drinks from real DynamoDB
- [ ] Quiz submits and returns ranked recommendations
- [ ] Review submission works end-to-end (POST to Lambda → Gemini → DynamoDB update)
- [ ] Taste profile updates after review

---

## Rollback

If something goes wrong:

```bash
# Delete the CloudFormation stack (removes Lambda + API Gateway but NOT DynamoDB)
# DynamoDB has DeletionPolicy: Retain so data is safe
aws cloudformation delete-stack \
  --stack-name matcha-scout-prod \
  --region us-east-1

# To delete DynamoDB table manually (destructive — only if sure):
# aws dynamodb delete-table --table-name matcha_scout --region us-east-1
```

---

## Cost check after deployment

```bash
# Check Lambda invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=matcha-scout-api-prod \
  --start-time $(date -u -v-1d +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 \
  --statistics Sum \
  --region us-east-1
```

For a portfolio project with light traffic, this should stay well within the free tier.
