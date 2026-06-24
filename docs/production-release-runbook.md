# Deep Research production release runbook

This is the authoritative release procedure for the June 24, 2026 Matcha Scout
Deep Research milestone.

Current production:

- Frontend: Next.js on Vercel
- Backend: FastAPI on Vercel Functions
- Database: Neon PostgreSQL

Stop immediately if any command reports blocked operations, unexpected count
drift, a local-looking production host, or a database environment mismatch.

## 1. Preflight

Run the complete local verification:

```bash
docker compose exec -T api pytest -q
(cd frontend && npm run lint && npm run build)
PYTHONPATH=backend python3 -m app.ingest.validate_research_artifacts \
  data/research/sd-matcha-cafes-2026-06-24.json \
  data/research/sd-matcha-verified-drinks-2026-06-24.json
git diff --check
```

Local reconciliation must be clean:

```bash
docker compose exec -T -e DATABASE_ENVIRONMENT=local api \
  python -m app.ingest.sync_deep_research \
  --local --remove-excluded
```

## 2. Load production credentials without printing them

Use the configured production Neon `DATABASE_URL`. Never echo it or pass it as a
literal command-line argument.

One local option that reads only `DATABASE_URL` without evaluating the rest of
the dotenv file is:

```bash
export DATABASE_URL="$(
  python3 - <<'PY'
from pathlib import Path
for line in Path(".env").read_text().splitlines():
    if line.startswith("DATABASE_URL="):
        print(line.split("=", 1)[1].strip().strip("\"'"))
        break
PY
)"
```

Confirm only non-secret metadata through the sync script; it prints the sanitized
database host and `DATABASE_ENVIRONMENT`, never credentials.

## 3. Read-only production reconciliation and backup

This command performs no database writes. It creates a timestamped, gitignored
JSON backup and reconciliation report under `data/backups/`.

```bash
docker run --rm \
  -e DATABASE_URL \
  -e DATABASE_ENVIRONMENT=production \
  -v "$PWD/backend/app:/app/app:ro" \
  -v "$PWD/data:/app/data" \
  matcha-scout-api \
  python -m app.ingest.sync_deep_research \
    --production \
    --remove-excluded \
    --write-backup
```

Expected production plan:

- 44 cafés matched
- 0 cafés created
- 13 café metadata updates
- 10 drinks created
- 18 drink evidence updates
- 2 drinks soft-excluded
- 0 taste profiles imported
- 0 external ratings imported
- 0 blocked operations

Any count drift is reported. Production apply refuses count drift.

## 4. Review the backup

The backup contains every affected café or drink partition, including taste
profiles and Matcha Scout reviews. It records before and planned values.

```bash
python3 -m json.tool data/backups/deep-research-production-<timestamp>.json >/dev/null
```

Keep the backup until post-release verification is complete. Do not commit it.

## 5. Deployment order

1. Deploy backend code first so nullable prices and soft exclusions are supported.
2. Deploy frontend code so nullable-price and status displays are supported.
3. Re-run read-only production reconciliation.
4. Apply the database reconciliation.
5. Run API and browser smoke tests.

Deployments require separate explicit authorization. This runbook does not
authorize deployment.

## 6. Production apply — DO NOT RUN YET

The non-interactive confirmation must match exactly:

```bash
docker run --rm \
  -e DATABASE_URL \
  -e DATABASE_ENVIRONMENT=production \
  -v "$PWD/backend/app:/app/app:ro" \
  -v "$PWD/data:/app/data" \
  matcha-scout-api \
  python -m app.ingest.sync_deep_research \
    --apply \
    --production \
    --confirm-production \
    --confirmation "APPLY MATCHA SCOUT DEEP RESEARCH TO PRODUCTION" \
    --remove-excluded
```

The script creates and verifies another backup immediately before the first write.

## 7. Verification

```bash
BASE="https://matcha-scout-api.vercel.app"
curl "$BASE/health"
curl "$BASE/cafes/yelp-pixshlytcxxnrh3veczjba" | python3 -m json.tool
curl "$BASE/cafes/yelp-pixshlytcxxnrh3veczjba/drinks" | python3 -m json.tool
curl "$BASE/drinks/review-targets?region_key=san-diego" | python3 -m json.tool
```

Confirm:

- Bopomofo has five visible current drinks with unknown prices shown as null.
- Excluded seasonal Bopomofo records are hidden.
- Existing review counts and reviewed taste profiles are unchanged.
- Newly created drinks are unrated.
- No `$0.00` placeholder appears.
- Vercel runtime error logs remain clean.

## 8. Rollback

Dry-run rollback first:

```bash
docker run --rm \
  -e DATABASE_URL \
  -e DATABASE_ENVIRONMENT=production \
  -v "$PWD/backend/app:/app/app:ro" \
  -v "$PWD/data:/app/data" \
  matcha-scout-api \
  python -m app.ingest.rollback_deep_research \
    --backup /app/data/backups/deep-research-production-<timestamp>.json \
    --production
```

Production rollback — DO NOT RUN unless explicitly authorized:

```bash
docker run --rm \
  -e DATABASE_URL \
  -e DATABASE_ENVIRONMENT=production \
  -v "$PWD/backend/app:/app/app:ro" \
  -v "$PWD/data:/app/data" \
  matcha-scout-api \
  python -m app.ingest.rollback_deep_research \
    --backup /app/data/backups/deep-research-production-<timestamp>.json \
    --apply \
    --production \
    --confirm-production \
    --confirmation "ROLL BACK MATCHA SCOUT DEEP RESEARCH PRODUCTION"
```

Rollback restores only metadata changed by this sync. A created drink is not
removed if it gained a Matcha Scout review or a non-neutral profile after the
backup. Metadata changed after the sync is also blocked rather than overwritten.

## Recovery limitations

- This workflow is an application-level backup, not a replacement for Neon
  point-in-time restore.
- Rollback intentionally stops on post-release edits instead of clobbering them.
- Reviews created after backup are never deleted.
- Production soft exclusions are restored by metadata rollback.
