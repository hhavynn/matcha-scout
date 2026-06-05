# Local Kubernetes

Phase 9 adds a local-only Kubernetes path for learning, demos, and resume proof. It runs Matcha Scout in a kind cluster on your machine.

This is not a production deployment. It does not use AWS EKS, does not change the live AWS Lambda/API Gateway/DynamoDB backend, and does not change the Vercel frontend. Production still runs on AWS Lambda + API Gateway + DynamoDB and Vercel.

## Why This Exists

Local Kubernetes is useful here because it shows the same operational building blocks you would use in larger systems:

- Deployments for long-running app processes
- Services for stable in-cluster networking
- ConfigMaps and Secrets for environment configuration
- Local image build and cluster image loading
- Port-forwarding for local smoke tests

The manifests are intentionally beginner-friendly and demo-sized.

## Required Tools

- Docker Desktop
- kubectl
- kind

Install missing Kubernetes tools with Homebrew:

```bash
brew install kubectl
brew install kind
```

Verify:

```bash
docker --version
kubectl version --client
kind version
```

## Files

The local manifests live in `k8s/local/`:

- `namespace.yaml`
- `configmap.yaml`
- `secret.example.yaml`
- `dynamodb-deployment.yaml`
- `dynamodb-service.yaml`
- `api-deployment.yaml`
- `api-service.yaml`
- `frontend-deployment.yaml`
- `frontend-service.yaml`

The helper script is `scripts/k8s-local.sh`.

## Validated Workflow

The local kind workflow was validated on June 5, 2026 with:

- Docker `29.5.2`
- kubectl client `v1.34.1`
- kind `v0.32.0`

The working command sequence was:

```bash
docker build -t matcha-scout-api:local ./backend
docker build -t matcha-scout-frontend:local ./frontend
kind create cluster --name matcha-scout-local
kind load docker-image matcha-scout-api:local --name matcha-scout-local
kind load docker-image matcha-scout-frontend:local --name matcha-scout-local
kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/
kubectl exec -n matcha-scout-local deploy/matcha-scout-api -- python -m app.seed.create_tables
kubectl exec -n matcha-scout-local deploy/matcha-scout-api -- python -m app.seed.seed_data
```

The helper script was also validated for:

```bash
scripts/k8s-local.sh status
scripts/k8s-local.sh apply
scripts/k8s-local.sh seed
```

## Create The Cluster

```bash
kind create cluster --name matcha-scout-local
```

If the cluster already exists, reuse it:

```bash
kind get clusters
```

Or use the helper:

```bash
scripts/k8s-local.sh create-cluster
```

## Build Local Images

From the repo root:

```bash
docker build -t matcha-scout-api:local ./backend
docker build \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  -t matcha-scout-frontend:local ./frontend
```

The frontend public API URL is intentionally `http://localhost:8000` because the browser calls the API through `kubectl port-forward`. Server-rendered Next.js pages use `SERVER_API_BASE_URL=http://matcha-scout-api:8000` inside Kubernetes.

Helper:

```bash
scripts/k8s-local.sh build-images
```

## Load Images Into kind

kind cannot automatically see every local Docker image. Load both images:

```bash
kind load docker-image matcha-scout-api:local --name matcha-scout-local
kind load docker-image matcha-scout-frontend:local --name matcha-scout-local
```

Helper:

```bash
scripts/k8s-local.sh load-images
```

## Apply Manifests

```bash
kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/
kubectl get pods -n matcha-scout-local
kubectl get svc -n matcha-scout-local
```

Apply the namespace first so beginner-friendly directory applies do not race namespace creation on a fresh cluster.

Wait until all pods are `Running` and ready.

Helper:

```bash
scripts/k8s-local.sh apply
scripts/k8s-local.sh status
```

## Seed DynamoDB Local

DynamoDB Local runs in memory inside the cluster. Data resets when the pod is deleted.

Seed only the local Kubernetes DynamoDB instance:

```bash
kubectl exec -n matcha-scout-local deploy/matcha-scout-api -- python -m app.seed.create_tables
kubectl exec -n matcha-scout-local deploy/matcha-scout-api -- python -m app.seed.seed_data
```

Helper:

```bash
scripts/k8s-local.sh seed
```

These commands run inside the API pod, which is configured with:

```bash
DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
DYNAMODB_TABLE_NAME=matcha_scout
USE_MOCK_AI=true
```

They do not seed production AWS.

## Port-Forward And Smoke Test

Open one terminal for the API:

```bash
kubectl port-forward -n matcha-scout-local svc/matcha-scout-api 8000:8000
```

Then in another terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/cafes
curl http://localhost:8000/drinks
curl "http://localhost:8000/recommendations?matcha_strength=5&sweetness=2&creaminess=3&earthiness=5&bitterness=3&price_max=8&milk_type=oat&limit=5"
```

Expected API smoke results:

- `/health` returns `{"status":"ok","service":"matcha-scout-api"}`
- `/cafes` returns 5 cafes
- `/drinks` returns 10 drinks
- `/recommendations` returns ranked results

Open one terminal for the frontend:

```bash
kubectl port-forward -n matcha-scout-local svc/matcha-scout-frontend 3000:3000
```

Then in another terminal:

```bash
curl -I http://localhost:3000
curl -I http://localhost:3000/drinks
curl -I http://localhost:3000/quiz
```

Expected frontend smoke results:

- `/` returns HTTP 200
- `/drinks` returns HTTP 200
- `/quiz` returns HTTP 200

Visit `http://localhost:3000` in a browser.

Helper commands:

```bash
scripts/k8s-local.sh port-forward-api
scripts/k8s-local.sh port-forward-frontend
```

## Tear Down

Delete only the local kind cluster:

```bash
kind delete cluster --name matcha-scout-local
```

Helper:

```bash
scripts/k8s-local.sh delete
```

This does not affect AWS, Vercel, or Docker Compose.

## Troubleshooting

### ImagePullBackOff

The cluster cannot find a local image.

Fix:

```bash
docker build -t matcha-scout-api:local ./backend
docker build --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 -t matcha-scout-frontend:local ./frontend
kind load docker-image matcha-scout-api:local --name matcha-scout-local
kind load docker-image matcha-scout-frontend:local --name matcha-scout-local
kubectl rollout restart deployment/matcha-scout-api -n matcha-scout-local
kubectl rollout restart deployment/matcha-scout-frontend -n matcha-scout-local
```

### Pod CrashLoopBackOff

Inspect logs and describe the pod:

```bash
kubectl get pods -n matcha-scout-local
kubectl logs -n matcha-scout-local deploy/matcha-scout-api
kubectl describe pod -n matcha-scout-local -l app.kubernetes.io/name=matcha-scout-api
```

For frontend issues, replace `matcha-scout-api` with `matcha-scout-frontend`.

### API Cannot Reach DynamoDB

Check that the DynamoDB pod and service exist:

```bash
kubectl get pods -n matcha-scout-local -l app.kubernetes.io/name=dynamodb-local
kubectl get svc dynamodb-local -n matcha-scout-local
kubectl logs -n matcha-scout-local deploy/dynamodb-local
```

The API must have:

```bash
DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
```

### Frontend Cannot Reach API

Make sure the API port-forward is running:

```bash
kubectl port-forward -n matcha-scout-local svc/matcha-scout-api 8000:8000
curl http://localhost:8000/health
```

The frontend image is built for browser access through `http://localhost:8000`. Server-rendered pages use `SERVER_API_BASE_URL=http://matcha-scout-api:8000` from the local Kubernetes ConfigMap.

### Port Already In Use

Stop the process using the port, or forward to a different local port:

```bash
kubectl port-forward -n matcha-scout-local svc/matcha-scout-api 18000:8000
kubectl port-forward -n matcha-scout-local svc/matcha-scout-frontend 13000:3000
```

If you use different local ports, update the frontend build argument before rebuilding the frontend image.
