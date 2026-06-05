"""
AWS Lambda entry point for the Matcha Scout FastAPI application.

Mangum wraps the ASGI app so API Gateway HTTP API can invoke it as a Lambda function.
The existing Uvicorn path (used by Docker in local development) is unchanged.

Local dev:  docker compose up  →  uvicorn app.main:app
AWS Lambda: API Gateway  →  lambda_handler.handler  →  Mangum(app)
"""
from mangum import Mangum
from app.main import app

# API Gateway HTTP API v2 (payload format version 2.0)
handler = Mangum(app, lifespan="off")
