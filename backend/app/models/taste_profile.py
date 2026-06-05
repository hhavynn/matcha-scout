from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


def compute_confidence(review_count: int) -> tuple[str, float]:
    """Return (label, score) based solely on Matcha Scout review count.

    Yelp ratings and external excerpts never influence this value — it
    reflects how reliable the *taste profile* data is, not business popularity.
    """
    if review_count >= 5:
        return ("high", 0.9)
    elif review_count >= 2:
        return ("medium", 0.65)
    elif review_count == 1:
        return ("low", 0.35)
    else:
        return ("unrated", 0.1)


class TasteProfile(BaseModel):
    drink_id: str
    matcha_strength: float = Field(ge=1.0, le=5.0)
    sweetness: float = Field(ge=1.0, le=5.0)
    creaminess: float = Field(ge=1.0, le=5.0)
    earthiness: float = Field(ge=1.0, le=5.0)
    bitterness: float = Field(ge=1.0, le=5.0)
    review_count: int = 0
    last_updated: datetime
    confidence_label: Optional[str] = None
    confidence_score: Optional[float] = None
