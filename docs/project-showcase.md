# Matcha Scout Project Showcase

## Elevator Pitch

Matcha Scout is an AI-powered matcha discovery app that helps users find cafe drinks matching their taste preferences. It combines natural-language review parsing, deterministic recommendation scoring, a polished Next.js frontend, and a deployed AWS serverless backend.

## Problem It Solves

Matcha menus are hard to compare because taste is subjective and reviews are usually unstructured. One person's "good matcha" might mean strong and grassy; another person's might mean sweet, creamy, and beginner-friendly. Matcha Scout turns that subjective language into structured taste profiles and ranks drinks against what the user actually likes.

## What Makes It More Than CRUD

- Free-text reviews are parsed into structured taste dimensions.
- Recommendations are ranked with a deterministic similarity engine, not hidden LLM judgment.
- Results include match percentages and plain-language reasons.
- The same app runs locally with Docker Compose, in a local kind cluster, and in production on Vercel + AWS.
- The data model supports cafes, drinks, reviews, taste profiles, and recommendation queries.

## Technical Architecture

The frontend is a Next.js App Router application deployed to Vercel. It fetches from a FastAPI backend running on AWS Lambda through API Gateway. DynamoDB stores fictional cafes, drinks, reviews, and aggregated taste profiles. Mangum adapts the ASGI FastAPI app to Lambda.

Local development uses Docker Compose with the API and DynamoDB Local. A separate local Kubernetes path uses kind, ClusterIP services, and local Docker images for DevOps practice without creating cloud Kubernetes resources.

## AI Structured-Output Flow

Users submit natural-language reviews such as "bold and grassy with a creamy oat finish, barely sweet." The parser converts that text into structured values:

- matcha strength
- sweetness
- creaminess
- earthiness
- bitterness
- confidence
- tags

Gemini structured output is supported. The deployed backend currently defaults to mock AI mode to keep production safe and cost-controlled while preserving the same data shape.

## Recommendation Scoring Flow

The quiz collects five preference dimensions plus optional filters like price and milk type. The backend compares those preferences against each drink's taste profile, applies filtering, ranks candidates, and returns:

- drink and cafe metadata
- match score and match percentage
- taste profile
- reasons explaining why the drink fits

This keeps the recommender explainable and testable.

## AWS Deployment Summary

The backend is deployed with AWS SAM to:

- API Gateway HTTP API
- Lambda running FastAPI through Mangum
- DynamoDB table `matcha_scout_prod`

The deployment is intentionally cost-conscious. It avoids EKS, RDS, EC2, NAT Gateway, and always-on infrastructure.

## Docker And Local Kubernetes Summary

Docker Compose supports local backend development with DynamoDB Local. Phase 9 added local-only Kubernetes manifests for kind:

- namespace
- ConfigMap
- placeholder Secret
- DynamoDB Local deployment/service
- API deployment/service
- frontend deployment/service

The kind workflow was validated end to end: image build, image load, manifest apply, seeding, API port-forward smoke tests, and frontend port-forward smoke tests.

## Testing And Validation

- 29 backend pytest tests for parsing and ranking behavior
- frontend ESLint
- Next.js production build
- curl smoke tests against production Vercel and AWS API URLs
- kind pod/service rollout checks

## What I Would Improve Next

- Enable Gemini in production after adding tighter rate limits and monitoring.
- Add CI/CD for tests, lint, build, and deployment previews.
- Add real user feedback flow and moderation for submitted drinks/reviews.
- Add analytics for recommendation usage and failed searches.
- Tighten IAM permissions and add stronger operational dashboards.
