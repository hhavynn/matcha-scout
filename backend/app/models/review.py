from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewCreate(BaseModel):
    drink_id: str
    raw_text: str = Field(min_length=10, max_length=2000)


class ParsedTasteProfile(BaseModel):
    matcha_strength: int = Field(ge=1, le=5)
    sweetness: int = Field(ge=1, le=5)
    creaminess: int = Field(ge=1, le=5)
    earthiness: int = Field(ge=1, le=5)
    bitterness: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


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


class ReviewResponse(BaseModel):
    id: str
    drink_id: str
    raw_text: str
    parsed_strength: int
    parsed_sweetness: int
    parsed_creaminess: int
    parsed_earthiness: int
    parsed_bitterness: int
    confidence: float
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    submitted_at: datetime
