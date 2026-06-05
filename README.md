# Matcha Scout

An AI-powered matcha discovery and recommendation app. Submit free-text reviews; Gemini Flash parses them into structured taste profiles. A deterministic weighted scoring engine ranks drinks against your preferences — no guessing, fully explainable.

> **Sample data notice:** All cafe names, drink names, prices, and descriptions are entirely fictional and for demonstration purposes only.

---

## What's built

| Phase | What it covers |
|---|---|
| **1** | FastAPI + DynamoDB Local + Docker Compose backend skeleton |
| **2** | AI review parsing with Gemini Flash + mock parser + taste profile aggregation |
| **3** | Deterministic recommendation/ranking engine with weighted scoring |
| **4** | Next.js 16 frontend — landing page, preference quiz, drinks browser, drink detail + review form |

---

## Running locally

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Node.js 20+ installed

### 1. Clone and enter the project
```bash
git clone <repo-url>
cd matcha-scout
```

### 2. Start the backend
```bash
# Copy and configure environment
cp .env.example .env
# .env defaults use mock AI mode — no Gemini key needed

# Start API + DynamoDB Local
docker compose up --build -d

# First-time setup (run once after fresh start)
docker compose exec api python -m app.seed.create_tables
docker compose exec api python -m app.seed.seed_data
```

The API is now running at `http://localhost:8000`.

### 3. Start the frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Visit: **http://localhost:3000**

> **Important:** The backend must be running before starting the frontend.

---

## Environment variables

### Backend (`.env` in repo root)
```
AWS_REGION=us-east-1
DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
DYNAMODB_TABLE_NAME=matcha_scout
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local

# Use mock AI parser (no API key needed):
USE_MOCK_AI=true

# Or use Gemini Flash:
USE_MOCK_AI=false
GEMINI_API_KEY=your_key_here
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Frontend pages

| Page | URL | Description |
|---|---|---|
| Landing | `/` | Hero, how it works, call to action |
| Quiz | `/quiz` | Preference sliders → ranked recommendations |
| Drinks | `/drinks` | Browse all drinks with cafe names |
| Drink detail | `/drinks/[id]` | Taste profile bars, reviews, submit review |

---

## Backend API

### Core endpoints
```bash
GET  /health
GET  /cafes
GET  /cafes/{id}
GET  /drinks
GET  /drinks/{id}
GET  /drinks/{id}/taste-profile
GET  /drinks/{id}/reviews
POST /reviews
GET  /recommendations
```

### Recommendation examples
```bash
# Strong, earthy, oat milk, max $8
curl "http://localhost:8000/recommendations?matcha_strength=5&sweetness=2&creaminess=3&earthiness=5&bitterness=3&price_max=8&milk_type=oat&limit=5"

# Sweet and creamy beginner
curl "http://localhost:8000/recommendations?matcha_strength=2&sweetness=5&creaminess=5&earthiness=2&bitterness=1&limit=3"
```

### Interactive docs
```
http://localhost:8000/docs
```

---

## Tests
```bash
# Backend (runs inside Docker)
docker compose exec api python -m pytest tests/ -v

# Frontend build verification
cd frontend && npm run build
cd frontend && npm run lint
```

---

## Project structure

```
matcha-scout/
├── backend/
│   ├── app/
│   │   ├── core/          # Config (settings from env vars)
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # FastAPI routes
│   │   ├── services/      # DynamoDB client, AI parser, aggregator, ranker
│   │   └── seed/          # Table creation + seed data
│   ├── tests/             # 29 pytest unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # Shared UI components
│   ├── lib/               # API client + TypeScript types
│   └── .env.example
├── docker-compose.yml
└── .env.example
```

---

## Development notes

- Backend hot-reloads via Docker volume mount — no rebuild needed for code changes
- Rebuild after `requirements.txt` changes: `docker compose up --build`
- DynamoDB data is in-memory — re-run `create_tables` + `seed_data` after `docker compose down`
- Frontend is Next.js 16 App Router — server components fetch data directly, client components handle interactivity only
- AWS is **not required** for local development — everything runs in Docker and Node

---

## Troubleshooting

**Docker not running**
Start Docker Desktop, then re-run `docker compose up --build -d`.

**Frontend can't connect to backend (drinks page shows error)**
1. Confirm backend is healthy: `curl http://localhost:8000/health`
2. Confirm `frontend/.env.local` contains `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
3. Restart `npm run dev` after editing `.env.local`

**Drinks/reviews missing (DynamoDB data wiped)**
Every `docker compose down` wipes the in-memory DynamoDB. Re-run:
```bash
docker compose exec api python -m app.seed.create_tables
docker compose exec api python -m app.seed.seed_data
```

**Gemini key missing (`USE_MOCK_AI=false` but no key)**
The API returns a 500 with: *"Gemini is not configured. Set GEMINI_API_KEY..."*
Either add your key to `.env`, or set `USE_MOCK_AI=true` for local dev.

**Full QA checklist**
See [`docs/local-qa-checklist.md`](docs/local-qa-checklist.md) for browser-by-browser testing steps and screenshot guidance.
