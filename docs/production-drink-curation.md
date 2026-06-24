# Production Drink Curation Guide

Current production architecture:

- Frontend: Next.js on Vercel
- Backend: FastAPI on Vercel Functions
- Database: Neon PostgreSQL

The AWS/DynamoDB curation workflow is historical. Current production writes use
the guarded PostgreSQL ingestion scripts and must be preceded by local validation.

## Required review checklist

- Every drink has a primary verification source.
- Exact menu names are preserved.
- Unknown price and temperature values remain `null`.
- Café IDs match production.
- No user reviews or community taste profiles are overwritten.
- Local dry-run, local apply, API checks, pytest, lint, and build all pass.
- A read-only production reconciliation has no blocked operations.
- A verified pre-write backup and rollback command are available.

## Ordinary manual curation

Validate:

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --dry-run
```

Apply locally:

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --apply --local
```

Production use requires a production Neon `DATABASE_URL`,
`DATABASE_ENVIRONMENT=production`, and the script's production confirmation
flags. For the Deep Research milestone, use the authoritative release runbook:
[production-release-runbook.md](production-release-runbook.md).

## Verification

```bash
BASE="https://matcha-scout-api.vercel.app"
curl "$BASE/cafes/<cafe_id>/drinks" | python3 -m json.tool
curl "$BASE/drinks/<drink_id>/taste-profile" | python3 -m json.tool
```

New verified drinks must begin as `unrated` with zero Matcha Scout reviews.
Neutral initialization values are display placeholders and are not eligible for
recommendations until a real Matcha Scout review exists.

## Never do this

- Import a drink from Yelp, Google, Beli, or old social posts.
- Convert an unknown price to zero.
- Replace a reviewed taste profile with neutral values.
- Delete user-submitted or reviewed drinks.
- print or commit a database connection string.
- Run an older script that writes to local and production in one invocation.
