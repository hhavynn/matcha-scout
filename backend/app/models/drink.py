from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DrinkCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    milk_options: Optional[List[str]] = None
    is_iced: Optional[bool] = None
    is_hot: Optional[bool] = None


class Drink(BaseModel):
    id: str
    cafe_id: str
    name: str
    description: str
    price: Optional[float] = None
    milk_options: List[str]
    is_iced: Optional[bool] = None
    is_hot: Optional[bool] = None
    image_url: Optional[str] = None
    created_at: datetime
    source: Optional[str] = None
    verification_status: Optional[str] = None
    verification_source: Optional[str] = None
    verification_url: Optional[str] = None
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    catalog_status: Optional[str] = None
    exclusion_reason: Optional[str] = None
    excluded_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    submitted_by_session: Optional[str] = None


class ReviewTargetDrink(Drink):
    cafe_name: str
    cafe_location: Optional[str] = None
    region_key: Optional[str] = None
    region_label: Optional[str] = None
    review_count: int = 0
    confidence_label: str
    confidence_score: float
