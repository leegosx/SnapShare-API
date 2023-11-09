from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from src.schemas.tag import Tag


class PhotoBase(BaseModel):
    id: Optional[int] = None
    image_url: str
    content: str
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[Tag] = []

    class Config:
        form_attributes = True


# Pydantic модель для створення нового Photo (без ID і часових відміток)
class PhotoCreate(BaseModel):
    image_url: str
    content: str
    tags: List[int] = []


class PhotoUpdate(BaseModel):
    content: str


class PhotoResponse(BaseModel):
    id: int
    image_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: int
    tags: List[Tag]

    class Config:
        from_attributes = True
