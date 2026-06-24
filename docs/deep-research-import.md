# Deep Research import workflow

This workflow reconciles the June 24, 2026 San Diego research artifacts with the local Matcha Scout database.

Dry-run is the default. Local apply remains supported. Production support is
guarded by environment, host, exact-confirmation, backup, and count-drift checks.
See `docs/production-release-runbook.md`; do not run production apply without
explicit authorization.

## Artifacts

- `data/research/sd-matcha-cafes-2026-06-24.json`
- `data/research/sd-matcha-verified-drinks-2026-06-24.json`
- `data/research/sd-matcha-cafe-match-report-2026-06-24.md`
- `data/research/sd-matcha-audit-2026-06-24.md`

## Dry run

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.sync_deep_research --remove-excluded
```

The `--remove-excluded` flag only previews removal of records explicitly marked `excluded`. A removal is blocked if the drink is not admin-curated or has any Matcha Scout reviews.

The strict drink file can also be validated independently with the standard curation tool:

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.manual_drink_curation \
  --file data/research/sd-matcha-verified-drinks-2026-06-24.json \
  --dry-run
```

## Apply locally

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.sync_deep_research \
  --apply --local --remove-excluded
```

Local apply writes a verified backup under `data/backups/` before the first
database mutation.

Re-run the dry run after applying. A clean result reports all cafés and drinks as unchanged.

## API verification

```bash
curl http://localhost:8000/cafes/yelp-pixshlytcxxnrh3veczjba \
  | python3 -m json.tool

curl http://localhost:8000/cafes/yelp-pixshlytcxxnrh3veczjba/drinks \
  | python3 -m json.tool

curl "http://localhost:8000/recommendations?matcha_strength=4&sweetness=2&creaminess=3&earthiness=4&bitterness=3" \
  | python3 -m json.tool
```

## Additive model changes

No SQL migration is required because the current PostgreSQL adapter stores entities in JSONB. The API models now support:

- nullable drink prices;
- `verified_at` on drinks;
- `business_status` and `status_note` on cafés.

Unknown menu prices are stored as `null`, never `0`. Neutral taste-profile placeholders remain available for display, but recommendation queries exclude profiles with `review_count: 0`.

## Production

Read-only production reconciliation is supported with `--production`. Production
writes additionally require `--apply --production --confirm-production` and the
exact typed confirmation. Follow `docs/production-release-runbook.md`.
