# Production Yelp Ingestion Guide

High-coverage ingestion of real cafe metadata from the official Yelp Fusion API
into the production DynamoDB table (`matcha_scout_prod`).

> **Safe by default.** The script always requires explicit opt-in flags to write.
> Dry-run is the default. Production writes require three explicit flags.

## API Call Math

| Operation | Calls per run |
|---|---|
| Search (1 city × 1 term, 50 results) | 1 call |
| Paginated search (2 pages) | 2 calls |
| Reviews endpoint | +1 call per cafe |

### Why skip reviews during bulk ingestion

Review excerpts are stored separately from Matcha Scout taste data and do **not** improve
confidence scores. Fetching them multiplies API calls by N×cafes. For a 150-cafe run with
reviews, that's 150+ extra calls vs. 0 without. Skip reviews during bulk ingestion and fetch
them individually later if needed.

### Staying within the 5,000-call trial limit

| Run | Estimated calls |
|---|---|
| SD: 6 terms × 10 locations, 1 page each | ~60 |
| OC: 6 terms × 15 locations, 1 page each | ~90 |
| Total for both regions (no reviews) | ~150 |
| With `--max-api-calls 500` per region | Never exceeds 500 |

The `--max-api-calls` flag is a hard stop that prevents exceeding the budget.
Recommended: 500 per region, leaving ~4,000 unused monthly calls for local testing.

## Preflight Checklist

- [ ] `.env` has `YELP_API_KEY` (not committed)
- [ ] Zero-spend AWS budget alert is configured
- [ ] `sam` CLI is authenticated with AWS
- [ ] Docker is running (for dry-run verification only)
- [ ] No production DynamoDB changes from the day before that need rollback

## Dry-Run Commands (no writes)

Dry-run is always safe — it calls Yelp Search but writes nothing.

### San Diego dry-run
```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region san-diego \
  --term-set matcha-discovery \
  --target-per-region 150 \
  --max-api-calls 100 \
  --high-coverage \
  --no-reviews \
  --dry-run \
  --request-delay 0.6
```

### Orange County dry-run
```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county \
  --term-set matcha-discovery \
  --target-per-region 150 \
  --max-api-calls 100 \
  --high-coverage \
  --no-reviews \
  --dry-run \
  --request-delay 0.6
```

### Assess dry-run quality

Good quality signals:
- Business names and categories match tea/coffee/matcha/boba/dessert types
- Addresses are within the expected region
- Duplicates across term/location combos are being skipped
- Total API calls are well under max

Bad quality signals (do not apply):
- Many businesses with unrelated categories (restaurants, salons, etc.)
- Addresses outside the region
- HTTP 429 errors (reduce `--request-delay`)

## Production Apply Commands

Only run these after a clean dry-run. All three of `--apply --production --confirm-production`
are required — the script refuses to write without all three.

### San Diego production apply
```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region san-diego \
  --term-set matcha-discovery \
  --target-per-region 150 \
  --max-api-calls 500 \
  --high-coverage \
  --no-reviews \
  --apply \
  --production \
  --confirm-production \
  --request-delay 0.6
```

### Orange County production apply
```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county \
  --term-set matcha-discovery \
  --target-per-region 150 \
  --max-api-calls 500 \
  --high-coverage \
  --no-reviews \
  --apply \
  --production \
  --confirm-production \
  --request-delay 0.6
```

Note: Production apply does **not** require Docker Compose (`DYNAMODB_ENDPOINT_URL` is
not needed — boto3 uses the Lambda/AWS credential chain to reach `matcha_scout_prod`).
Run from a machine with AWS credentials configured (e.g., your local terminal with `aws configure`).

## Verification Commands

After apply, verify production:

```bash
BASE="https://2bd8jfknuc.execute-api.us-west-2.amazonaws.com"

# Total cafes
curl "$BASE/cafes" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d), 'total')"

# By region
curl "$BASE/cafes?region_key=san-diego" | python3 -c "import sys,json; print(len(json.load(sys.stdin)), 'SD')"
curl "$BASE/cafes?region_key=orange-county" | python3 -c "import sys,json; print(len(json.load(sys.stdin)), 'OC')"

# Spot-check a cafe
curl "$BASE/cafes/<cafe_id>" | python3 -m json.tool
```

Frontend verification:

```bash
curl -I https://matcha-scout.vercel.app/cafes
```

Open the browser and confirm:
- `/cafes` with "San Diego" filter shows SD cafes
- `/cafes` with "Orange County" filter shows OC cafes
- Cafe cards show Yelp badge, rating, address
- Cafe detail page loads for a Yelp-sourced cafe
- Empty state shown for cafes with no drinks (no fabricated data)

## Troubleshooting

### HTTP 429 Too Many Requests

Increase `--request-delay` to 1.0 or 1.5 seconds.
Reduce `--max-api-calls` to limit concurrent pressure.

### Missing cafes in some cities

Yelp `best_match` sorts by relevance — a city with fewer matcha cafes may return 0
results for some search terms. This is expected; deduplication handles it.

### Unexpected write error

Check AWS credentials: `aws sts get-caller-identity`
Check DynamoDB table name is `matcha_scout_prod`.
Check Lambda/IAM role has write access to the table.

## What ingestion does NOT do

- Does NOT add matcha drink items — those require manual curation or user submission
- Does NOT affect confidence scores — only Matcha Scout reviews do that
- Does NOT overwrite existing Matcha Scout reviews
- Does NOT call the Yelp AI API
- Does NOT scrape Yelp pages (only the official Fusion REST API is used)

## After Ingestion

1. Verify counts via the API.
2. Open `data/curation/my-<region>-cafes-to-curate.local.md` and add verified drinks.
3. Run `manual_drink_curation.py` to add drinks (see `docs/manual-drink-curation.md`).
4. User submissions via the `/cafes/[id]` frontend page will also populate drinks.
