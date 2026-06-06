# Production Drink Curation Guide

How to safely add verified matcha drinks to the production catalog.

> **Start small.** Apply 10–25 verified drinks before any bulk run.
> Every drink must have a verification source — no guessed entries.

## Required review checklist

Before applying drinks to production, confirm:

- [ ] Each drink entry has a `verification_source` and ideally a `verification_url`
- [ ] Drink names are copied from official menus, not paraphrased from Yelp reviews
- [ ] Prices are from the menu; `null` is fine if unknown
- [ ] `cafe_id` matches a real cafe in production (`GET /cafes` to confirm)
- [ ] Dry-run passes with no errors
- [ ] Local apply passes on Docker Compose
- [ ] Local API (`GET /cafes/{id}/drinks`) shows the drinks correctly

## Step A — Generate curation checklist

```bash
python -m app.ingest.export_curation_targets \
  --region san-diego --source production \
  --limit 50 --sort relevance \
  --output data/curation/my-san-diego-production-curation.local.md
```

Open the file and use the Yelp URLs to find cafe websites and menus.
Record verified drinks in the checklist table.

## Step B — Fill the curation JSON

```bash
cp data/curation/verified-drinks.example.json data/curation/my-san-diego-drinks.json
# Edit the file — only add drinks you can cite a source for
```

See `docs/manual-drink-curation.md` for field descriptions.

## Step C — Dry-run (no writes)

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --dry-run
```

Verify:
- `CREATE` lines for each new drink
- `NO CAFE` should be empty (fix any bad cafe_ids first)
- `INVALID` should be empty (fix validation errors first)

## Step D — Local apply

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --apply --local
```

Then verify locally:
```bash
curl http://localhost:8000/cafes/<cafe_id>/drinks | python3 -m json.tool
```

Check:
- `source` = `"admin_curated"`
- `verification_status` = `"admin_curated"` or `"admin_verified"`
- Taste profile: `review_count: 0`, `confidence_label: "unrated"`

## Step E — Production apply

Only after local validation passes:

```bash
python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json \
  --apply --production --confirm-production
```

> Note: Run from the host machine (not Docker container) so AWS credentials are used.
> The container's `DYNAMODB_ENDPOINT_URL` points to local DynamoDB.

## Step F — Production verification

```bash
BASE="https://2bd8jfknuc.execute-api.us-west-2.amazonaws.com"

# List drinks for a specific cafe
curl "$BASE/cafes/<cafe_id>/drinks" | python3 -m json.tool

# Check recommendations now include the new drink
curl "$BASE/recommendations?matcha_strength=4&sweetness=2&creaminess=3&earthiness=4&bitterness=3" \
  | python3 -c "import sys,json; [print(r['drink_name'], r['match_pct']) for r in json.load(sys.stdin)]"
```

Open https://matcha-scout.vercel.app/cafes/<cafe_id> and confirm the drink appears
with "Unrated" confidence badge and an empty taste profile.

## What NOT to do

- Do not add drinks from Yelp review text ("someone mentioned a matcha latte")
- Do not add drinks from Instagram or Google Maps
- Do not add drinks you have not personally seen on an official source
- Do not run `--allow-overwrite` on the first batch — let the default no-overwrite protect existing data
- Do not deploy AWS or Vercel for drink curation — ingestion scripts write directly to DynamoDB

## Recommended first batch

**5–10 cafes, 1–3 drinks each = 10–25 total drinks.**

Suggested priority cafes (San Diego):
- Matcha Cafe Maiko (multiple locations, matcha specialist)
- Holy Matcha (dedicated matcha bar)
- Kyoto Coast Matcha (India St, dedicated matcha)
- Yun Tea House (high rating, Convoy)
- Urban Matcha (Convoy)

Suggested priority cafes (Orange County):
- Junbi Matcha & Tea (Irvine, dedicated matcha)
- Airoma Cafe (Fountain Valley, highly rated)
- besa Coffee & Matcha (Santa Ana, matcha-forward)
- HNTea Organic Tea House (multiple OC locations)
- CHAGEE Modern Teahouse (Mission Viejo)

## After applying drinks

1. Drinks start with `confidence_label: "unrated"` (0 Matcha Scout reviews).
2. As users visit the cafe and submit reviews via `/cafes/{id}`, confidence improves.
3. Yelp ratings never affect confidence — only Matcha Scout reviews count.
4. The quiz page will start recommending these drinks once they have taste profiles from reviews.
