from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PreferenceQuery(BaseModel):
    id: str
    strength_pref: int = Field(ge=1, le=5)
    sweetness_pref: int = Field(ge=1, le=5)
    creaminess_pref: int = Field(ge=1, le=5)
    earthiness_pref: int = Field(ge=1, le=5)
    bitterness_pref: int = Field(ge=1, le=5)
    price_max: Optional[float] = None
    milk_type: Optional[str] = None
    session_id: Optional[str] = None
    submitted_at: datetime
