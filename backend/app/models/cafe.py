from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Cafe(BaseModel):
    id: str
    name: str
    location: str
    address: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    source: Optional[str] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    categories: Optional[list[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    price: Optional[str] = None
    last_ingested_at: Optional[datetime] = None
    region_key: Optional[str] = None
    region_label: Optional[str] = None
    is_popup: Optional[bool] = None
    beli_rating: Optional[float] = None
    menu_url: Optional[str] = None
    menu_summary: Optional[str] = None
    menu_verified_at: Optional[datetime] = None
    ceremonial_matcha: Optional[bool] = None
    research_label: Optional[str] = None
    business_status: Optional[str] = None
    status_note: Optional[str] = None


class ExternalReviewExcerpt(BaseModel):
    id: str
    cafe_id: str
    source: str
    excerpt: str
    rating: Optional[float] = None
    author_name: Optional[str] = None
    time_created: Optional[datetime] = None
    external_url: Optional[str] = None
    ingested_at: datetime
