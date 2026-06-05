from pydantic import BaseModel, Field
from datetime import datetime


class TasteProfile(BaseModel):
    drink_id: str
    matcha_strength: float = Field(ge=1.0, le=5.0)
    sweetness: float = Field(ge=1.0, le=5.0)
    creaminess: float = Field(ge=1.0, le=5.0)
    earthiness: float = Field(ge=1.0, le=5.0)
    bitterness: float = Field(ge=1.0, le=5.0)
    review_count: int = 0
    last_updated: datetime
