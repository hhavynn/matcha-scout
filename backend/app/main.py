from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, cafes, drinks, reviews, recommendations

app = FastAPI(
    title="Matcha Scout API",
    description="Discover and explore matcha drinks based on your taste preferences.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cafes.router)
app.include_router(drinks.router)
app.include_router(reviews.router)
app.include_router(recommendations.router)
