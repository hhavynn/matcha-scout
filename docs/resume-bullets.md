# Resume Bullets

## A. SWE Internship Version

- Built and deployed Matcha Scout, an AI-powered matcha recommendation app using Next.js, TypeScript, FastAPI, DynamoDB, AWS Lambda/API Gateway, and Vercel.
- Implemented a deterministic ranking engine that scores drinks across 5 taste dimensions and returns explainable match percentages, filters, and recommendation reasons.
- Added production and local DevOps workflows, including Docker Compose, AWS SAM deployment, and verified kind Kubernetes manifests for local cluster demos.

## B. Backend / Cloud-Heavy Version

- Developed a FastAPI backend for cafe/drink recommendations with Pydantic models, DynamoDB single-table access patterns, review ingestion, taste profile aggregation, and recommendation APIs.
- Deployed the backend on AWS Lambda behind API Gateway with Mangum and DynamoDB, using cost-conscious serverless architecture instead of EC2, RDS, EKS, or NAT Gateway.
- Validated backend behavior with 29 pytest tests covering mock AI parsing, aggregation, ranking, filtering, and recommendation result structure.

## C. AI / Product-Heavy Version

- Built an AI-assisted product experience that parses natural-language matcha reviews into structured taste dimensions for strength, sweetness, creaminess, earthiness, and bitterness.
- Combined Gemini-compatible structured output with deterministic recommendation scoring so results remain explainable, reproducible, and testable.
- Designed a polished Next.js frontend with a preference quiz, ranked recommendations, drink browsing, detail pages, and review submission.

## D. DevOps / Kubernetes-Heavy Version

- Added Docker Compose local development and Dockerfiles for a full-stack FastAPI/Next.js/DynamoDB Local application.
- Authored local-only Kubernetes manifests for kind, including namespace, ConfigMap, Secret example, deployments, services, image loading, seeding, and port-forward smoke tests.
- Verified the local Kubernetes workflow end to end by building images, loading them into kind, applying manifests, seeding DynamoDB Local, and testing API/frontend routes.

## E. Ultra-Compressed 2-Bullet Version

- Built and deployed an AI-powered matcha recommender with Next.js, FastAPI, DynamoDB, AWS Lambda/API Gateway, Vercel, and Gemini-compatible structured review parsing.
- Implemented explainable recommendation scoring plus Docker Compose and verified kind Kubernetes workflows, with backend behavior covered by 29 pytest tests.
