# Manual Drink Curation

## How to pick cafes to curate first

With 150+ cafes per region in production, you cannot verify all of them at once.
Use the **curation priority export script** to generate a ranked checklist:

```bash
# From local DynamoDB (Docker running):
docker compose exec api python -m app.ingest.export_curation_targets \
  --region san-diego --source local \
  --limit 50 --sort relevance \
  --output data/curation/my-san-diego-production-curation.local.md

# From production DynamoDB (AWS credentials, no DYNAMODB_ENDPOINT_URL):
python -m app.ingest.export_curation_targets \
  --region san-diego --source production \
  --limit 50 --sort relevance \
  --output data/curation/my-san-diego-production-curation.local.md
```

The script ranks cafes by "curation priority" — a heuristic based on name/category keywords
("matcha", "tea rooms", "bubble tea", "japanese dessert") weighted by popularity. It is not a
recommendation quality score; it helps you spend verification time on the most relevant venues.

The output file is gitignored. Do not commit it.

## How to use the production curation checklist

Open `data/curation/my-san-diego-production-curation.local.md`. For each cafe:

1. Check the Yelp URL to find the cafe's menu or website link.
2. Navigate to the cafe's **own website** (not Yelp) and find the menu.
3. If a matcha drink appears on the official menu, record it in the checklist table.
4. Once you have 10–25 verified entries, fill `data/curation/my-san-diego-drinks.json`.
5. Run `manual_drink_curation.py --dry-run` to validate.
6. Apply locally, verify via the API, then follow `docs/production-drink-curation.md`.

## Why exact drinks are manually curated

Yelp gives Matcha Scout real San Diego cafe metadata, but it does not give reliable exact
matcha drink information. A Yelp review might mention "the matcha latte" in passing, but that
is not the same as knowing the drink's name, price, milk options, or iced/hot availability.

Exact drinks are user-submitted or manually curated. A manually curated drink is one that
an admin has personally verified from a reliable source before adding it. This keeps the
catalog trustworthy and avoids fabricating menu items.

## What counts as verified

A drink entry is appropriate for the curation file if it came from one of:

- The cafe's official website or online menu
- A personal visit where you ordered the drink
- A user submission you can independently confirm
- A printed or physical menu from the cafe

## What does NOT count as verified

Do not add entries based on:

- Guessing from a Yelp review mention ("someone said they had a matcha latte")
- Scraped social media posts or Instagram captions
- Unverified Beli or Google Maps text
- Another person's memory without a primary source

If you are unsure, leave the entry out. A shorter, trustworthy catalog is better than a
longer, fabricated one.

## How to fill out the curation JSON file

Copy the example template and create your own file:

```bash
cp data/curation/san-diego-drinks.example.json data/curation/my-san-diego-drinks.json
```

The file must be a JSON object with a `"drinks"` array. Each entry supports:

| Field | Required | Notes |
|---|---|---|
| `cafe_external_source` + `cafe_external_id` | One of these | For Yelp-ingested cafes: `"yelp"` + the Yelp business ID |
| `cafe_id` | or this | For seed data cafes: direct ID like `"cafe-001"` |
| `cafe_name_hint` | No | Informational only; not used for matching |
| `name` | Yes | Drink name, max 120 chars |
| `description` | No | Short description; leave null if unsure |
| `price` | No | Positive number; leave null if unknown |
| `milk_options` | No | List of strings, e.g. `["oat","whole"]`; normalized to lowercase |
| `is_iced` | No | Default: `true` |
| `is_hot` | No | Default: `false` |
| `verification_status` | No | Default: `"admin_curated"`; use `"admin_verified"` once personally confirmed |
| `verification_source` | Yes for real entries | `"official_menu"`, `"personal_visit"`, `"cafe_website"`, or `"user_submission"` |
| `verification_url` | When available | Official menu/source URL; use `null` for an in-person-only source |
| `verification_notes` | Yes for real entries | Date, source checked, and any useful audit notes |

Example:

```json
{
  "version": 1,
  "source_note": "SD cafes verified from official menus, June 2026.",
  "drinks": [
    {
      "cafe_external_source": "yelp",
      "cafe_external_id": "the-yelp-id-from-ingestion",
      "cafe_name_hint": "Bird Rock Coffee Roasters",
      "name": "Iced Matcha Latte",
      "description": "House matcha over oat milk, lightly sweetened.",
      "price": 7.00,
      "milk_options": ["oat", "whole", "almond"],
      "is_iced": true,
      "is_hot": true,
      "verification_status": "admin_verified",
      "verification_source": "official_menu",
      "verification_url": "https://example.com/official-menu",
      "verification_notes": "Verified from the cafe website menu, June 2026."
    }
  ]
}
```

To find the correct Yelp ID for a cafe after ingestion:

```bash
curl http://localhost:8000/cafes | python3 -m json.tool | grep -A3 '"source": "yelp"'
```

## Full local workflow

### Step A — Start local stack

```bash
docker compose up --build -d
docker compose exec api python -m app.seed.create_tables
docker compose exec api python -m app.seed.seed_data
```

### Step B — Ingest SD cafes from Yelp (dry-run first)

Add `YELP_API_KEY=your_key_here` to local `.env` only. Do not commit the key.

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 10 --term matcha --location "San Diego, CA" \
  --include-reviews --dry-run
```

### Step C — Apply Yelp cafes locally

```bash
docker compose exec api python -m app.ingest.yelp_san_diego \
  --limit 20 --term matcha --location "San Diego, CA" \
  --include-reviews --apply --local
```

### Step D — Identify cafe IDs and create curation file

```bash
curl http://localhost:8000/cafes | python3 -m json.tool
```

Copy `data/curation/san-diego-drinks.example.json` to a new file (e.g.
`data/curation/my-san-diego-drinks.json`). The `.gitignore` inside `data/curation/`
prevents personal curation files from being committed.

### Step E — Dry-run the curation

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --dry-run
```

Expected output:
- `CREATE` lines for new drinks at known cafes
- `NO CAFE` lines for unresolved cafes (run Yelp ingestion first)
- `SKIP` lines for drinks that already exist
- Summary at the end

### Step F — Apply locally

```bash
docker compose exec api python -m app.ingest.manual_drink_curation \
  --file data/curation/my-san-diego-drinks.json --apply --local
```

### Step G — Verify

```bash
curl http://localhost:8000/cafes/<cafe_id>/drinks | python3 -m json.tool
```

Check that:
- `source` is `"admin_curated"`
- `verification_status` is `"admin_curated"` or `"admin_verified"`
- Taste profile has `review_count: 0` and `confidence_label: "unrated"`

Or open [http://localhost:3000/cafes](http://localhost:3000/cafes) in the browser.

## Confidence and trust

A manually curated drink starts with `review_count: 0` and `confidence_label: "unrated"`.
This is correct — the drink exists in the catalog, but no one has reviewed its *taste* yet.

Confidence improves only when Matcha Scout community reviews come in. Yelp ratings and
review counts never affect confidence. This keeps taste data trustworthy.

| review_count | confidence |
|:---:|:---:|
| 0 | Unrated |
| 1 | Low |
| 2–4 | Medium |
| 5+ | High |

## Verification status field

| Value | Meaning |
|---|---|
| `"admin_curated"` | Added by admin; source not yet fully confirmed |
| `"admin_verified"` | Admin has personally confirmed from a primary source |
| `"unverified"` | User-submitted; not yet reviewed |
| `"community_reviewed"` | Future: enough community reviews to trust the entry |

## How to fill the verified-drinks JSON

Copy `data/curation/verified-drinks.example.json` to a real file (e.g.
`data/curation/my-san-diego-drinks.json`). For each drink you have personally verified:

| Field | Notes |
|---|---|
| `cafe_id` | From the curation checklist or `GET /cafes` output |
| `name` | Exact name from the official menu (copy-paste, do not paraphrase) |
| `price` | From the menu; leave `null` if unknown |
| `milk_options` | List from the menu (e.g. `["whole", "oat", "almond"]`) |
| `is_iced` / `is_hot` | What options the menu actually offers |
| `verification_source` | `"official_menu"`, `"personal_visit"`, `"cafe_website"`, or `"user_submission"` |
| `verification_url` | Paste the menu URL or leave `null` for in-person visit |
| `verification_notes` | Date, what you saw, any notes |

**Do not add a drink if you cannot cite a verification source.**

## Production drink curation process

See [docs/production-drink-curation.md](production-drink-curation.md) for the full
production apply workflow. In summary:

1. Generate curation checklist → verify 10–25 drinks offline → fill JSON file
2. Dry-run: `manual_drink_curation.py --dry-run`
3. Apply locally and verify via `GET /cafes/{id}/drinks`
4. Future production apply: `manual_drink_curation.py --apply --production --confirm-production`
5. Verify via production API: `GET https://2bd8jfknuc.../cafes/{id}/drinks`

Do not bulk-upload guessed drinks. Start with 10–25 well-verified entries.

## Future production process

Production curation infrastructure is guarded by `--production --confirm-production`.
Before applying:

1. Complete and verify the local curation file.
2. Run `pytest` and dry-run.
3. Apply locally and verify endpoints.
4. Apply to production only after local validation passes.

## What Yelp/Beli scraping is not used

Scraping violates Yelp's and Beli's terms of service and produces unreliable, unlicensed data.
The official Yelp Fusion API is used only for business metadata (names, addresses, ratings).
Taste data — the core of Matcha Scout — always comes from real user reviews and verified
manual curation.
