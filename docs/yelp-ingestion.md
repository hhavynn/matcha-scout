# Yelp San Diego Cafe Ingestion

Phase 11 adds a local/admin ingestion path for real San Diego cafe metadata using the official Yelp Fusion API.

This does not scrape Yelp, Beli, Google Maps, or any browser-rendered pages. Beli, if used later, should be manual future input only; no scraping.

## Why The Official Yelp API

The Yelp Fusion API provides a legitimate way to search businesses and retrieve limited business metadata. Matcha Scout uses it to seed real San Diego cafes while keeping Matcha Scout user reviews and taste profiles separate.

## Yelp API Limits

- Business Search returns business metadata such as name, address, categories, rating, review count, image URL, phone, price, and Yelp URL.
- Yelp Reviews returns up to 3 review excerpts per business.
- Those excerpts are external source metadata, not Matcha Scout reviews.
- Matcha Scout taste profiles are still based on Matcha Scout user-submitted reviews, not Yelp excerpts.

## Get A Yelp Fusion API Key

1. Create or open a Yelp Fusion developer app.
2. Copy the Yelp Fusion API key.
3. Put it only in local `.env`.

Root `.env` example:

```bash
YELP_API_KEY=your_local_key_here
YELP_API_BASE_URL=https://api.yelp.com/v3
YELP_DEFAULT_LOCATION=San Diego, CA
YELP_DEFAULT_TERM=matcha
```

Do not commit real API keys.

## Local Safety Rules

- Ingestion defaults to dry-run.
- `--apply` is required to write.
- `--apply` also requires `--local`.
- Apply mode refuses to run unless `DYNAMODB_ENDPOINT_URL` is set, which keeps Phase 11 local-only.
- The script never deletes data.
- Yelp review excerpts are stored separately under `EXTERNAL_REVIEW#YELP#...`, never under Matcha Scout `REVIEW#...` items.
- Existing user reviews and taste profiles are not overwritten.

## Start Local DynamoDB

```bash
docker compose up --build -d
docker compose exec api python -m app.seed.create_tables
docker compose exec api python -m app.seed.seed_data
```

## Dry Run

Dry-run is the default behavior unless `--apply` is passed:

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 5 \
  --term matcha \
  --location "San Diego, CA" \
  --include-reviews \
  --dry-run
```

If `YELP_API_KEY` is missing, the script exits cleanly with a message telling you to configure the key locally.

## Apply To Local DynamoDB

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 10 \
  --term matcha \
  --location "San Diego, CA" \
  --include-reviews \
  --apply \
  --local
```

Use `--no-overwrite` if you want to preserve existing user-owned cafe fields such as name, address, website, and created timestamp while still refreshing Yelp metadata.

## Verify

```bash
curl http://localhost:8000/cafes
```

Look for cafes with:

```json
{
  "source": "yelp",
  "external_id": "...",
  "external_url": "https://www.yelp.com/..."
}
```

If external excerpts were included:

```bash
curl http://localhost:8000/cafes/<cafe_id>/external-reviews
```

## Data Separation

Yelp metadata can live on cafe records:

- `source`
- `external_id`
- `external_url`
- `rating`
- `review_count`
- `image_url`
- `categories`
- `coordinates`
- `phone`
- `price`
- `last_ingested_at`

Yelp excerpts are stored separately:

```text
PK = CAFE#<cafe_id>
SK = EXTERNAL_REVIEW#YELP#<review_id_or_index>
```

Matcha Scout user reviews remain separate:

```text
PK = DRINK#<drink_id>
SK = REVIEW#...
```

Only Matcha Scout user reviews contribute to drink taste profiles.

## Orange County Ingestion

Orange County uses a multi-city search strategy to get broad coverage.
The script searches Irvine, Costa Mesa, Garden Grove, and other OC cities,
deduplicates by Yelp business ID, and caps at `--limit`.

```bash
# OC dry-run
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county --limit 20 --term matcha \
  --include-reviews --dry-run --request-delay 0.6

# OC apply locally
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county --limit 20 --term matcha \
  --include-reviews --apply --local --request-delay 0.6
```

For San Diego (single location):

```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region san-diego --limit 20 --term matcha \
  --include-reviews --apply --local --request-delay 0.6
```

See [docs/regions-and-location.md](regions-and-location.md) for the complete
region strategy, rate-limit guidance, and how to add new regions.

## Full San Diego Curation Workflow

After Yelp ingestion, use the manual curation script to add verified exact drinks.
See [docs/manual-drink-curation.md](manual-drink-curation.md) for the complete workflow.

### Step A — Yelp dry-run

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 10 --term matcha --location "San Diego, CA" \
  --include-reviews --dry-run
```

### Step B — Yelp apply locally

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 20 --term matcha --location "San Diego, CA" \
  --include-reviews --apply --local
```

### Step C — Create curation file with verified drinks

```bash
cp data/curation/san-diego-drinks.example.json data/curation/my-san-diego-drinks.json
# Edit the file with real, verified drink data (see docs/manual-drink-curation.md)
```

Personal curation files (`my-*.json`, etc.) are gitignored via `data/curation/.gitignore`.

### Step D — Dry-run manual curation

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --dry-run
```

### Step E — Apply manual curation locally

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --apply --local
```

### Step F — Verify

```bash
# List SD cafes
curl http://localhost:8000/cafes | python3 -m json.tool

# Check drinks under a specific cafe
curl http://localhost:8000/cafes/<cafe_id>/drinks | python3 -m json.tool
```

## Future Direction

Yelp populates real cafe metadata. Exact matcha drink entries come from user submissions
or manual curation (see [docs/manual-drink-curation.md](manual-drink-curation.md)).
Production ingestion and curation writes will be supported in a future phase once
production write safety tooling is finalized.
