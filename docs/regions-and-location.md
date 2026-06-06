# Regions and Location Support

## Current supported regions

| Region | region_key | Yelp search strategy |
|---|---|---|
| San Diego | `san-diego` | Single search: `San Diego, CA` |
| Orange County | `orange-county` | Multi-city: Irvine, Costa Mesa, Garden Grove, Westminster, Orange, Anaheim, Fullerton, Huntington Beach, Newport Beach |

Seed data cafes (Portland, Seattle, SF, etc.) have no `region_key` and appear only in "All Regions" views.

## Manual region selector (current)

The app includes a region picker on the `/cafes` and `/quiz` pages:

- **All Regions** — shows all cafes regardless of location
- **San Diego** — shows cafes tagged `region_key: "san-diego"`
- **Orange County** — shows cafes tagged `region_key: "orange-county"`

Recommendations respect the selected region — when a region is chosen, only drinks from cafes in that region are scored and returned.

## Why geolocation is not enabled yet

Browser location services require user permission and introduce UX complexity (permission prompts, fallbacks, denials). For the current stage of the app, a manual region picker gives users full control without any privacy implications.

Geolocation will be added in a later phase once the catalog is large enough that proximity filtering matters meaningfully.

## How Yelp ingestion works per region

### San Diego

```bash
# Dry-run
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region san-diego --limit 20 --term matcha \
  --include-reviews --dry-run --request-delay 0.6

# Apply locally
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region san-diego --limit 20 --term matcha \
  --include-reviews --apply --local --request-delay 0.6
```

### Orange County (multi-city)

For OC, the script automatically searches across multiple cities to get
broad coverage. Results are deduplicated by Yelp business ID.

```bash
# Dry-run (9 cities searched, up to 20 unique results)
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county --limit 20 --term matcha \
  --include-reviews --dry-run --request-delay 0.6

# Apply locally
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county --limit 20 --term matcha \
  --include-reviews --apply --local --request-delay 0.6
```

To search a specific OC city only:

```bash
docker compose exec api python -m app.ingest.yelp_region_ingestion \
  --region orange-county --location "Irvine, CA" \
  --limit 10 --term matcha --dry-run
```

### Rate limiting

`--request-delay 0.6` adds 0.6 seconds between each review-excerpt API call
to respect Yelp's per-second rate limit. Reduce to 0.5 if running single-city
searches. Increase to 1.0 if you see HTTP 429 errors.

## Why exact drink data still requires manual verification

Yelp gives Matcha Scout real cafe metadata — names, addresses, ratings — but
not reliable drink-level data. A Yelp review might mention "the matcha latte"
but that is not the same as a verified menu item.

After ingesting cafes from Yelp, verified drinks must be added via:

1. **User submissions** — anonymous users can submit drinks via the UI.
2. **Manual curation** — fill in `data/curation/my-<region>-drinks.json` with
   drinks verified from official menus, cafe websites, or personal visits, then
   run `python -m app.ingest.manual_drink_curation --apply --local`.

See [docs/manual-drink-curation.md](manual-drink-curation.md) for the full workflow.

## Adding a new region

1. Add the `region_key` to `REGION_MAP` in `backend/app/services/regions.py`.
2. Add default search locations to a new constant (if multi-city).
3. Add the `--region` choice to `yelp_region_ingestion.py`.
4. Add the region to `REGIONS` in `frontend/lib/types.ts`.
5. No database migration needed — region fields are optional on all records.
