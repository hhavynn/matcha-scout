# Manual Drink Curation

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
| `curation_notes` | No | Free text; ignored by the script; useful for your own records |

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
      "curation_notes": "Verified from their website menu, June 2026."
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

## Future production process

Production curation is not automated in this phase. When ready:

1. Complete and verify the local curation file.
2. Run a full local validation (`pytest`, dry-run, apply, verify endpoints).
3. Deploy the updated backend to AWS.
4. Run the curation script against production DynamoDB with appropriate flags
   (to be added in a future phase when production write safety is fully implemented).

Do not run production writes until that tooling is in place.

## What Yelp/Beli scraping is not used

Scraping violates Yelp's and Beli's terms of service and produces unreliable, unlicensed data.
The official Yelp Fusion API is used only for business metadata (names, addresses, ratings).
Taste data — the core of Matcha Scout — always comes from real user reviews and verified
manual curation.
