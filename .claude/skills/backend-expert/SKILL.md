---
name: backend-expert
description: Expertise in FastAPI, Python backend logic, API endpoints, Pydantic schemas, and data adapters.
---

# Backend Expert Skill

This skill is designed for the Backend Expert agent. It handles Python backend development, FastAPI routing, endpoint design, business logic, data models, and Yelp search/manual curation ingestion workflows.

## Guidelines & Responsibilities

1. **FastAPI & Routing**:
   - Build API routes inside `backend/app/routers/` and register them in `backend/app/main.py`.
   - Adhere to the REST API schema detailed in the documentation (`GET /cafes`, `GET /recommendations`, `POST /cafes/{id}/drinks-with-review`, etc.).
   - Implement clean dependency injection for database sessions and services.

2. **Pydantic Schemas & Types**:
   - Use Pydantic v2 schemas to validate inputs and outputs.
   - Organize validation and model response schemas under `backend/app/models/` or routers as needed.
   - Implement robust error handling and HTTP status codes.

3. **Data Ingestion**:
   - Handle Yelp Fusion API search and manual drink ingestion script development (`backend/app/ingest/`).
   - Standardize data ingestion tasks to run locally, loading Yelp results or static data into the database.
