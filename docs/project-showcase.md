# Matcha Scout Project Showcase

## Elevator Pitch

Matcha Scout is an AI-powered matcha discovery app that helps users find cafe drinks matching their taste preferences. It combines natural-language review parsing, deterministic recommendation scoring, a polished Next.js frontend, and a FastAPI backend on Vercel Functions with Neon PostgreSQL.

## Problem It Solves

Matcha menus are hard to compare because taste is subjective and reviews are usually unstructured. One person's "good matcha" might mean strong and grassy; another person's might mean sweet, creamy, and beginner-friendly. Matcha Scout turns that subjective language into structured taste profiles and ranks drinks against what the user actually likes.

## What Makes It More Than CRUD

- Free-text reviews are parsed into structured taste dimensions.
- Recommendations are ranked with a deterministic similarity engine, not hidden LLM judgment.
- Results include match percentages and plain-language reasons.
- The same app runs locally with Docker Compose, in a local kind cluster, and in production on Vercel + Neon.
- The data model supports cafes, drinks, reviews, taste profiles, and recommendation queries.

## Technical Architecture

The frontend is a Next.js App Router application deployed to Vercel. It fetches from a FastAPI backend running on Vercel Functions. Neon PostgreSQL 17 stores café, drink, review, and aggregated taste-profile entities through a temporary JSONB compatibility layer.

Local development uses Docker Compose with the API and PostgreSQL 17. A separate historical local Kubernetes path uses kind and DynamoDB Local for DevOps practice; it is not the production architecture.

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

## Production Deployment Summary

- Next.js frontend on Vercel
- FastAPI backend on Vercel Functions
- Neon PostgreSQL 17 using a pooled serverless connection
- Mock AI parsing by default for safe, low-cost operation

The earlier AWS Lambda/API Gateway/DynamoDB deployment is retained in historical documentation only.

## Docker And Local Kubernetes Summary

Docker Compose supports local backend development with PostgreSQL 17. Phase 9 previously added local-only Kubernetes manifests for kind:

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
- curl smoke tests against both production Vercel projects
- kind pod/service rollout checks

## What I Would Improve Next

- Enable Gemini in production after adding tighter rate limits and monitoring.
- Add CI/CD for tests, lint, build, and deployment previews.
- Add real user feedback flow and moderation for submitted drinks/reviews.
- Add analytics for recommendation usage and failed searches.
- Add stronger production monitoring and release automation.
