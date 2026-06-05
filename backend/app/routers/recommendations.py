from fastapi import APIRouter, Query
from typing import Optional
from app.models.recommendation import RecommendationRequest, RecommendationResult
from app.services import db
from app.services.ranker import rank_drinks

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationResult])
def get_recommendations(
    matcha_strength: int = Query(ge=1, le=5),
    sweetness: int = Query(ge=1, le=5),
    creaminess: int = Query(ge=1, le=5),
    earthiness: int = Query(ge=1, le=5),
    bitterness: int = Query(ge=1, le=5),
    price_max: Optional[float] = Query(default=None, gt=0),
    milk_type: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
):
    prefs = RecommendationRequest(
        matcha_strength=matcha_strength,
        sweetness=sweetness,
        creaminess=creaminess,
        earthiness=earthiness,
        bitterness=bitterness,
        price_max=price_max,
        milk_type=milk_type,
        limit=limit,
    )

    drinks_with_profiles = db.get_all_drinks_with_profiles()
    cafes_by_id = db.get_all_cafes_by_id()

    return rank_drinks(prefs, drinks_with_profiles, cafes_by_id)
