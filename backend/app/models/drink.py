from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class DrinkCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    milk_options: Optional[List[str]] = None
    is_iced: bool = True
    is_hot: bool = False


class Drink(BaseModel):
    id: str
    cafe_id: str
    name: str
    description: str
    price: float
    milk_options: List[str]
    is_iced: bool
    is_hot: bool
    image_url: Optional[str] = None
    created_at: datetime
    source: Optional[str] = None
    verification_status: Optional[str] = None
    submitted_at: Optional[datetime] = None
    submitted_by_session: Optional[str] = None
