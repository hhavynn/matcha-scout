# Resume Bullets

## A. SWE Internship Version

- Built and deployed Matcha Scout, an AI-powered matcha recommendation app using Next.js, TypeScript, FastAPI on Vercel Functions, and Neon PostgreSQL.
- Implemented a deterministic ranking engine that scores drinks across 5 taste dimensions and returns explainable match percentages, filters, and recommendation reasons.
- Added production and local DevOps workflows including Vercel deployments, Neon-backed persistence, Docker Compose, CI, and verified kind manifests for local cluster demos.

## B. Backend / Cloud-Heavy Version

- Developed a FastAPI backend for café/drink recommendations with Pydantic models, Neon PostgreSQL persistence, review ingestion, taste-profile aggregation, and recommendation APIs.
- Deployed the backend on Vercel Functions with pooled Neon PostgreSQL and guarded, backup-first production data reconciliation.
- Validated backend behavior with 180+ pytest tests covering parsing, aggregation, ranking, ingestion safety, and API behavior.

## C. AI / Product-Heavy Version

- Built an AI-assisted product experience that parses natural-language matcha reviews into structured taste dimensions for strength, sweetness, creaminess, earthiness, and bitterness.
- Combined Gemini-compatible structured output with deterministic recommendation scoring so results remain explainable, reproducible, and testable.
- Designed a polished Next.js frontend with a preference quiz, ranked recommendations, drink browsing, detail pages, and review submission.

## D. DevOps / Kubernetes-Heavy Version

- Added Docker Compose local development and Dockerfiles for a full-stack FastAPI/Next.js/PostgreSQL application.
- Authored local-only Kubernetes manifests for kind, including namespace, ConfigMap, Secret example, deployments, services, image loading, seeding, and port-forward smoke tests.
- Verified the local Kubernetes workflow end to end by building images, loading them into kind, applying manifests, seeding DynamoDB Local, and testing API/frontend routes.

## E. Ultra-Compressed 2-Bullet Version

- Built and deployed an AI-powered matcha recommender with Next.js, FastAPI on Vercel Functions, Neon PostgreSQL, and Gemini-compatible structured review parsing.
- Implemented explainable recommendation scoring plus guarded research ingestion, Docker Compose, CI, and verified local kind workflows.
