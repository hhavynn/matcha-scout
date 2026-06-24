# Matcha Scout — Local QA Checklist

Use this before deploying the Vercel frontend/backend, applying a Neon
reconciliation, or recording a demo video.

---

## Prerequisites

All of these must be true before starting:

- [ ] Docker Desktop is running
- [ ] `docker compose ps` shows `matcha-api` and PostgreSQL as healthy
- [ ] Database migrations/schema setup have completed
- [ ] `docker compose exec api python -m app.seed.seed_data` has been run
- [ ] `cd frontend && npm run dev` is running at `http://localhost:3000`
- [ ] Backend tests pass: `docker compose exec -T api pytest -q`
- [ ] Frontend checks pass: `cd frontend && npm run lint && npm run build`
- [ ] Research artifacts pass `python3 -m app.ingest.validate_research_artifacts`

---

## Manual browser checklist

Open `http://localhost:3000` in a browser (Chrome or Safari recommended).

### Landing page `/`

- [ ] Page loads with a green matcha theme and 🍵 emoji
- [ ] "Start the Quiz →" button is visible and links to `/quiz`
- [ ] "Browse Drinks" button links to `/drinks`
- [ ] "Find My Match" button in the nav links to `/quiz`
- [ ] Footer shows the sample data notice
- [ ] Page is readable on mobile (resize window to ~375px)

### Browse drinks `/drinks`

- [ ] Page loads with the current visible drink catalog
- [ ] Each card shows: drink name, cafe name, price or "Price unavailable", description, milk tags
- [ ] Cards show "iced" / "hot" badges where appropriate
- [ ] Clicking a card navigates to that drink's detail route
- [ ] Soft-excluded drinks do not appear
- [ ] Page is readable on mobile (cards stack to single column)

### Drink detail

- [ ] A current drink route loads with its expected name, café, and price state
- [ ] Taste profile bars display (Matcha Strength, Sweetness, etc.)
- [ ] "Seed data — no reviews yet" message shows in taste profile section (before any reviews)
- [ ] Review form textarea is visible with placeholder text
- [ ] "Submit Review" button is visible but disabled (textarea is empty)
- [ ] Try a drink with oat milk — the "oat" tag shows

### Submitting a review

On a visible drink detail page:

1. Type a short review: `"Strong earthy ceremonial matcha, a little bitter but smooth"`
2. - [ ] "Submit Review" button becomes enabled after 10+ characters
3. Click "Submit Review"
4. - [ ] Button shows "Analyzing…" while loading
5. - [ ] Green success card appears with 5 parsed taste score boxes (1–5)
6. - [ ] Tags appear (e.g., "strong", "earthy", "ceremonial")
7. - [ ] Review count in taste profile increases from "Seed data" to "1 review"
8. - [ ] Taste bars visually update
9. - [ ] The new review appears in the "Community Reviews" section below
10. - [ ] Review text area clears after successful submission

### Review edge cases

- [ ] Submit a review < 10 characters → red "must be at least 10 characters" message appears, no API call
- [ ] Stop the backend (`docker compose stop api`) → submitting a review shows a user-friendly error, not a white crash page. Restart with `docker compose start api`

### Quiz page `/quiz`

- [ ] Page loads with 5 sliders (Matcha Strength, Sweetness, Creaminess, Earthiness, Bitterness)
- [ ] Each slider shows its current value (1–5) in a green badge
- [ ] "Max price" and "Milk preference" fields appear below sliders
- [ ] "Find My Matcha" button is at the bottom
- [ ] On mobile: sliders stack above results (not side-by-side)

### Quiz submission (no filters)

1. Leave all sliders at 3 (defaults)
2. Click "Find My Matcha"
3. - [ ] Spinner appears while loading
4. - [ ] Results appear showing drink cards with match percentages
5. - [ ] Each result shows: match % badge, drink name, cafe name, price, ✓ reasons, taste bars, milk tags
6. - [ ] "View details →" link works on each result
7. - [ ] Results are sorted highest match first

### Quiz submission (strong earthy user)

1. Set Matcha Strength = 5, Sweetness = 1, Earthiness = 5
2. Click "Find My Matcha"
3. - [ ] Strong, earthy drinks rank above sweet, mild drinks with otherwise equal filters

### Quiz submission (filters)

1. Set Max Price = 6.00
2. Click "Find My Matcha"
3. - [ ] Only drinks with known prices at or below $6.00 appear
   - Drinks with unknown prices must not bypass a maximum-price filter

4. Set Milk = "oat", Max Price = (blank)
5. Click "Find My Matcha"
6. - [ ] Only oat-milk drinks appear

### Quiz empty results

1. Set Max Price = 1.00 (impossible)
2. Click "Find My Matcha"
3. - [ ] "No drinks matched your filters" message appears with "Try relaxing your price or milk type filters."

---

## Screenshots to take (for README / resume)

1. **Landing page** — full desktop view showing hero section
2. **Drinks grid** — `/drinks` showing the current catalog in a 3-column layout
3. **Drink detail** — a current drink showing taste bars and empty review form
4. **Review submission result** — green success card with 5 parsed taste boxes and tags
5. **Quiz page** — sliders on left, recommendation results on right (desktop)
6. **Quiz recommendation card** — close-up showing match %, reasons, taste bars

---

## Common issues and fixes

### Backend won't start
```bash
docker compose down
docker compose up --build -d
```
Wait 10 seconds, then reseed:
```bash
docker compose exec api python -m app.seed.seed_data
```

### Drinks page shows "Could not load drinks"
The backend is not running or the API URL is wrong.
1. Check: `curl http://localhost:8000/health` — should return `{"status":"ok",...}`
2. Check: `cat frontend/.env.local` — should have `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
3. Restart the frontend dev server after editing `.env.local`

### Taste profile bars don't update after review
The backend may have returned stale data or the refresh failed silently. Refresh the browser page manually — the server will re-fetch the updated profile.

### PostgreSQL data missing
Check the PostgreSQL container and reseed local development data if appropriate:
```bash
docker compose ps
docker compose exec api python -m app.seed.seed_data
```

### Mock AI vs Gemini
The default `.env` has `USE_MOCK_AI=true`. The mock parser uses keywords to assign taste ratings. To use real Gemini:
```
USE_MOCK_AI=false
GEMINI_API_KEY=your_key_here
```
Then rebuild: `docker compose up --build -d`
