# Matcha Scout

An AI-powered matcha discovery app that helps you find matcha drinks based on your taste preferences: matcha strength, sweetness, creaminess, earthiness, bitterness, price, and milk type.

> **Sample data notice:** All cafe names, drink names, prices, and descriptions in this project are entirely fictional and created for demonstration purposes.

---

## Phase 1 — Backend Skeleton

This phase includes:
- FastAPI backend with read-only endpoints for cafes and drinks
- Single-table DynamoDB design with a GSI for querying drinks by cafe
- DynamoDB Local running via Docker (no AWS account needed)
- Fictional seed data: 5 cafes, 10 drinks, 10 taste profiles
- Hot-reloading dev server via Docker Compose volume mount

---

## Local setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone and enter the project
```bash
git clone <repo-url>
cd matcha-scout
```

### 2. Start services
```bash
docker compose up --build
```

This starts two containers:
- `matcha-api` on `http://localhost:8000`
- `matcha-dynamodb` (DynamoDB Local) on `localhost:8001`

### 3. Create the DynamoDB table
In a new terminal tab (while containers are running):
```bash
docker compose exec api python -m app.seed.create_tables
```

Expected output:
```
Table 'matcha_scout' created successfully.
```

### 4. Seed sample data
```bash
docker compose exec api python -m app.seed.seed_data
```

Expected output:
```
Seeding table 'matcha_scout'...
  Seeded cafe: Verdant Cup
  Seeded cafe: Umami House
  ...
  Seeded drink: Stone Garden Ceremonial
  ...
Seed complete.
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
```json
[
  {"id": "cafe-001", "name": "Verdant Cup", "location": "Portland, OR", ...},
  ...
]
```

### Get one cafe
```bash
curl http://localhost:8000/cafes/cafe-001
```
```json
{"id": "cafe-001", "name": "Verdant Cup", "location": "Portland, OR", ...}
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
│   │   ├── routers/       # FastAPI route handlers
│   │   ├── services/      # DynamoDB client wrapper
│   │   ├── seed/          # Table creation and sample data
│   │   └── main.py        # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Development notes

- Code changes in `backend/app/` are reflected immediately without rebuilding (volume mount + uvicorn `--reload`)
- To rebuild after changing `requirements.txt`: `docker compose up --build`
- To stop: `docker compose down`
- To wipe DynamoDB data (it's in-memory): `docker compose down` then `docker compose up`
