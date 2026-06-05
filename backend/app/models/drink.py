from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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
