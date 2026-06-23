# PostgreSQL Migration

Matcha Scout now supports PostgreSQL as its primary persistence backend while
temporarily retaining the DynamoDB adapter for legacy local tools.

Migration status: deployed June 23, 2026.

- Frontend: https://matcha-scout.vercel.app
- Backend: https://matcha-scout-api.vercel.app
- Database: Neon PostgreSQL 17

## Target

- PostgreSQL 17
- Neon Free plan
- Neon's pooled connection string
- FastAPI deployed as a separate Vercel Hobby project

PostgreSQL 17 is intentionally selected instead of PostgreSQL 18. Version 17 is
fully mature, widely supported by clients, and does not require any features
from the newest major release.

## Data Model

The first migration uses one `matcha_items` table with a JSONB document column.
It preserves the application's existing `PK`, `SK`, `GSI1PK`, and `GSI1SK`
access patterns, so API routes and ingestion workflows do not need a risky
simultaneous rewrite.

This is a compatibility migration, not the final normalized relational design.
Once production is stable, cafes, drinks, reviews, and taste profiles can be
split into typed relational tables behind the same database service module.

## Local Setup

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python -m app.seed.create_tables
docker compose exec api python -m app.seed.seed_data
curl http://localhost:8000/health
```

The local database uses PostgreSQL 17 and persists in the
`matcha-postgres-data` Docker volume.

## Neon Setup

1. Create a free Neon project using PostgreSQL 17.
2. Copy the pooled connection string (the hostname contains `-pooler`).
3. Add it to the backend Vercel project as `DATABASE_URL`.
4. Add these backend environment variables:

```text
DATABASE_TABLE_NAME=matcha_items
DATABASE_ENVIRONMENT=production
USE_MOCK_AI=true
CORS_ALLOWED_ORIGINS=https://matcha-scout.vercel.app
```

5. From the `backend` directory, pull production environment variables and
   initialize the schema:

```bash
vercel env pull .env.local
set -a
source .env.local
set +a
python -m app.seed.create_tables
python -m app.seed.seed_data
```

6. Deploy the `backend` directory as its own Vercel project.
7. Set the frontend project's `NEXT_PUBLIC_API_BASE_URL` and
   `SERVER_API_BASE_URL` to the new backend URL, then redeploy the frontend.

The production deployment uses `https://matcha-scout-api.vercel.app`.

## Restoring Real Cafe Data

The fictional seed restores a working demo immediately. Real cafe metadata can
then be rebuilt by rerunning the existing Yelp regional ingestion workflow,
followed by the verified-drink curation workflow.

## Rollback

Unset `DATABASE_URL` to use the legacy DynamoDB adapter. No route-level changes
are required because both backends implement the same database service API.
