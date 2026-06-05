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
