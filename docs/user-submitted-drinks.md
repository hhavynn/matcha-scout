# User-Submitted Drinks & Confidence Scoring

## Why exact drinks are user-submitted

Yelp gives Matcha Scout reliable cafe metadata — name, location, address, Yelp ratings — but
Yelp does **not** give reliable data about the exact matcha drinks a cafe serves or how those
drinks taste. Yelp review excerpts may mention matcha in passing, but they are neither structured
nor trustworthy enough to power taste-profile recommendations.

The only people who know exactly what a cafe's matcha drink tastes like are the people who have
ordered it. That is why Matcha Scout lets users add exact drinks they have tried and submit
reviews that describe the taste. These user-submitted records become the authoritative source of
taste profiles and recommendations.

## Yelp cafe metadata vs. Matcha Scout taste data

| What Yelp provides             | What Matcha Scout provides          |
|--------------------------------|-------------------------------------|
| Cafe name, location, address   | Exact drink names at a cafe          |
| Yelp rating (overall business) | Per-drink taste profiles (1–5 scale) |
| Yelp review count (popularity) | Community reviews parsed by AI       |
| Categories, hours, phone       | Recommendation matching scores       |
| External URL                   | Confidence scoring (Matcha Scout only) |

Yelp ratings and review counts reflect **business popularity**, not taste quality. They are
displayed on cafe pages as external context only and never influence Matcha Scout's taste
profiles or recommendation confidence scores.

## How confidence works

Confidence measures how reliable a drink's taste profile is, based solely on the number of
Matcha Scout reviews it has received:

| Review count | Confidence label | Score |
|:------------:|:----------------:|:-----:|
| 0            | Unrated          | 0.10  |
| 1            | Low              | 0.35  |
| 2–4          | Medium           | 0.65  |
| 5+           | High             | 0.90  |

**Key rules:**
- Yelp excerpts never increase confidence.
- Yelp ratings never influence confidence.
- Confidence reflects taste-profile reliability, not business popularity.
- A new user-submitted drink starts with a neutral taste profile (3.0 on all dimensions) and
  "Unrated" confidence. This signals to viewers that the profile is a placeholder.
- Confidence improves as community Matcha Scout reviews come in and the averages converge.

### How confidence affects recommendations

Confidence is a **tiebreaker only**, not the primary ranking signal. Drinks are ranked first by
`match_pct` (taste similarity to the user's preferences). Among drinks with identical match
scores, higher confidence ranks first. This prevents new drinks from being buried but also
prevents high-confidence drinks with poor taste matches from displacing genuinely good matches.

## How users can add a drink and review

1. Go to **Cafes** → find the cafe you visited.
2. On the cafe detail page, click **Add a drink**.
3. Fill in the drink name and optional fields (description, price, milk options, iced/hot).
4. Submit — the drink is created immediately with "Unrated" confidence.
5. You are directed to the drink detail page where you can write a review.
6. Your review text is parsed by the AI parser (mock or Gemini) into structured taste ratings.
7. The taste profile is recalculated from all reviews — confidence updates automatically.

No account is required. All submissions are anonymous.

## Why Yelp/Beli/Google Maps scraping is avoided

Scraping violates terms of service and produces unreliable data. Yelp's official Fusion API is
used only for the local ingestion script (`backend/app/ingest/yelp_san_diego.py`), which is an
admin-only operation. The Fusion API provides structured, licensed metadata about businesses —
not drink-level taste data. Matcha Scout's taste data is always user-generated.

## Source and verification fields

User-submitted drinks carry metadata to distinguish them from admin-curated seed data:

```json
{
  "source": "user_submitted",
  "verification_status": "unverified"
}
```

Possible future values:
- `source`: `"manual_seed"` (seed data), `"user_submitted"`, `"admin_curated"`
- `verification_status`: `"unverified"`, `"community_reviewed"`, `"admin_verified"`

These fields are stored but not currently used for filtering. They are available for future
moderation features.
