from pydantic import BaseModel, Field
from typing import Optional, List


class RecommendationRequest(BaseModel):
    matcha_strength: int = Field(ge=1, le=5)
    sweetness: int = Field(ge=1, le=5)
    creaminess: int = Field(ge=1, le=5)
    earthiness: int = Field(ge=1, le=5)
    bitterness: int = Field(ge=1, le=5)
    price_max: Optional[float] = Field(default=None, gt=0)
    milk_type: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    region_key: Optional[str] = None


class TasteProfileSnapshot(BaseModel):
    matcha_strength: float
    sweetness: float
    creaminess: float
    earthiness: float
    bitterness: float
    review_count: int
    confidence_label: Optional[str] = None
    confidence_score: Optional[float] = None


class RecommendationResult(BaseModel):
    drink_id: str
    drink_name: str
    cafe_id: str
    cafe_name: Optional[str] = None
    price: float
    milk_options: List[str]
    taste_profile: TasteProfileSnapshot
    match_score: float
    match_pct: int
    reasons: List[str]
    confidence_label: Optional[str] = None
    confidence_score: Optional[float] = None
