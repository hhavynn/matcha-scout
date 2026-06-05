#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="matcha-scout-local"
NAMESPACE="matcha-scout-local"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

create_cluster() {
  need kind
  if kind get clusters | grep -qx "$CLUSTER_NAME"; then
    echo "kind cluster '$CLUSTER_NAME' already exists; reusing it."
    return
  fi
  kind create cluster --name "$CLUSTER_NAME"
}

build_images() {
  need docker
  docker build -t matcha-scout-api:local "$ROOT_DIR/backend"
  docker build \
    --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
    -t matcha-scout-frontend:local "$ROOT_DIR/frontend"
}

load_images() {
  need kind
  kind load docker-image matcha-scout-api:local --name "$CLUSTER_NAME"
  kind load docker-image matcha-scout-frontend:local --name "$CLUSTER_NAME"
}

apply_manifests() {
  need kubectl
  kubectl apply -f "$ROOT_DIR/k8s/local/"
  kubectl rollout status deployment/dynamodb-local -n "$NAMESPACE"
  kubectl rollout status deployment/matcha-scout-api -n "$NAMESPACE"
  kubectl rollout status deployment/matcha-scout-frontend -n "$NAMESPACE"
}

seed_data() {
  need kubectl
  kubectl exec -n "$NAMESPACE" deploy/matcha-scout-api -- python -m app.seed.create_tables
  kubectl exec -n "$NAMESPACE" deploy/matcha-scout-api -- python -m app.seed.seed_data
}

status() {
  need kubectl
  kubectl get pods -n "$NAMESPACE"
  kubectl get svc -n "$NAMESPACE"
}

delete_cluster() {
  need kind
  kind delete cluster --name "$CLUSTER_NAME"
}

usage() {
  cat <<'USAGE'
Usage: scripts/k8s-local.sh <command>

Commands:
  create-cluster          Create or reuse the local kind cluster
  build-images            Build API and frontend local Docker images
  load-images             Load local Docker images into kind
  apply                   Apply k8s/local manifests and wait for rollouts
  seed                    Create and seed the local DynamoDB table
  port-forward-api        Forward http://localhost:8000 to the API service
  port-forward-frontend   Forward http://localhost:3000 to the frontend service
  status                  Show pods and services
  delete                  Delete the local kind cluster
USAGE
}

case "${1:-}" in
  create-cluster) create_cluster ;;
  build-images) build_images ;;
  load-images) load_images ;;
  apply) apply_manifests ;;
  seed) seed_data ;;
  port-forward-api) need kubectl; kubectl port-forward -n "$NAMESPACE" svc/matcha-scout-api 8000:8000 ;;
  port-forward-frontend) need kubectl; kubectl port-forward -n "$NAMESPACE" svc/matcha-scout-frontend 3000:3000 ;;
  status) status ;;
  delete) delete_cluster ;;
  *) usage; exit 1 ;;
esac
