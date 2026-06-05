from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Review(BaseModel):
    id: str
    drink_id: str
    raw_text: str
    parsed_strength: Optional[int] = None
    parsed_sweetness: Optional[int] = None
    parsed_creaminess: Optional[int] = None
    parsed_earthiness: Optional[int] = None
    parsed_bitterness: Optional[int] = None
    confidence: Optional[float] = None
    submitted_at: datetime
