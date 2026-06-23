---
name: qa-devops
description: Expertise in pytest testing, Docker Compose, Kubernetes kind manifests, linting, and deployments.
---

# QA & DevOps Expert Skill

This skill is designed for the QA & DevOps agent. It handles automated testing, linting, containerization, local Kubernetes setups, and production Vercel deployment verification.

## Guidelines & Responsibilities

1. **Testing & Linting**:
   - Run backend tests using `pytest` inside the `backend/` directory.
   - Ensure frontend builds pass ESLint checks (`npm run lint` or `npx eslint`).
   - Write comprehensive tests for new endpoints, schemas, and adapter layers.

2. **Docker Compose & K8s**:
   - Maintain and verify `docker-compose.yml` for local development.
   - Maintain and verify the Kubernetes manifests for the local `kind` cluster setup.
   - Ensure local dev environments match production behavior as closely as possible.

3. **Vercel Deployments**:
   - Manage frontend and backend Vercel configuration files (`vercel.json`).
   - Run smoke tests against deployed environments to confirm overall stability.
