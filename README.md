# Matcha Scout

An AI-powered matcha discovery app that helps you find matcha drinks based on your taste preferences: matcha strength, sweetness, creaminess, earthiness, bitterness, price, and milk type.

> **Sample data notice:** All cafe names, drink names, prices, and descriptions in this project are entirely fictional and created for demonstration purposes.

---

## Phase 1 — Backend Skeleton

- FastAPI backend with read-only endpoints for cafes and drinks
- Single-table DynamoDB design with a GSI for querying drinks by cafe
- DynamoDB Local running via Docker (no AWS account needed)
- Fictional seed data: 5 cafes, 10 drinks, 10 taste profiles
- Hot-reloading dev server via Docker Compose volume mount

## Phase 2 — AI Review Parsing

- `POST /reviews` — submit a free-text matcha review
- Gemini Flash parses the review into structured taste fields (strength, sweetness, creaminess, earthiness, bitterness)
- Reviews are stored in DynamoDB; the drink's aggregate taste profile is recalculated after each new review
- `GET /drinks/{id}/reviews` — list all reviews for a drink
- Mock AI mode for local development (no API key required)
- 10 pytest tests covering keyword parsing logic and aggregation math

---

## Local setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone and enter the project
```bash
git clone <repo-url>
cd matcha-scout
```

### 2. Configure environment
```bash
cp .env.example .env
```

For local development with the mock AI parser (no API key needed):
```
USE_MOCK_AI=true
```

To use Gemini (real AI parsing):
```
USE_MOCK_AI=false
GEMINI_API_KEY=your_key_here
```

### 3. Start services
```bash
docker compose up --build -d
```

This starts two containers:
- `matcha-api` on `http://localhost:8000`
- `matcha-dynamodb` (DynamoDB Local) on `localhost:8001`

### 4. Create the DynamoDB table (first time only)
```bash
docker compose exec api python -m app.seed.create_tables
```

### 5. Seed sample data
```bash
docker compose exec api python -m app.seed.seed_data
```

### 6. Run tests
```bash
docker compose exec api python -m pytest tests/ -v
```

---

## API endpoints

### Health check
```bash
curl http://localhost:8000/health
```
```json
{"status": "ok", "service": "matcha-scout-api"}
```

### List all cafes
```bash
curl http://localhost:8000/cafes
```

### Get one cafe
```bash
curl http://localhost:8000/cafes/cafe-001
```

### List all drinks
```bash
curl http://localhost:8000/drinks
```

### Filter drinks by cafe
```bash
curl "http://localhost:8000/drinks?cafe_id=cafe-001"
```

### Get one drink
```bash
curl http://localhost:8000/drinks/drink-001
```

### Get a drink's taste profile
```bash
curl http://localhost:8000/drinks/drink-001/taste-profile
```

### Submit a review (AI-parsed)
```bash
curl -X POST http://localhost:8000/reviews \
  -H "Content-Type: application/json" \
  -d '{"drink_id":"drink-001","raw_text":"This was a strong earthy ceremonial matcha, a little bitter but really smooth."}'
```

### List reviews for a drink
```bash
curl http://localhost:8000/drinks/drink-001/reviews
```

### Interactive API docs
```
http://localhost:8000/docs
```

---

## Project structure

```
matcha-scout/
├── backend/
│   ├── app/
│   │   ├── core/          # Config and settings
│   │   ├── models/        # Pydantic data models
│   │   ├── routers/       # FastAPI route handlers (health, cafes, drinks, reviews)
│   │   ├── services/      # DynamoDB client, AI parser, taste profile aggregator
│   │   ├── seed/          # Table creation and sample data scripts
│   │   └── main.py        # FastAPI app entry point
│   ├── tests/             # Pytest tests (mock parser, aggregation logic)
│   ├── pytest.ini
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example           # Committed — copy to .env and fill in values
└── README.md
```

---

## Development notes

- Code changes in `backend/app/` and `backend/tests/` reflect immediately without rebuilding (volume mount + uvicorn `--reload`)
- To rebuild after changing `requirements.txt`: `docker compose up --build`
- To stop: `docker compose down`
- To wipe DynamoDB data (it's in-memory): `docker compose down` then `docker compose up`, then re-run create_tables and seed_data
