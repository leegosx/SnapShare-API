from datetime import datetime
from typing import List, Optional, ClassVar
from pydantic import BaseModel, ConfigDict, validator

from src.schemas.tag import TagRequest


class ImageBase(BaseModel):
    id: Optional[int] = None
    image_url: str
    content: str
    user_id: int
    image_transformed_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[TagRequest] = []
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# Pydantic модель для створення нового image (без ID і часових відміток)
class ImageCreate(BaseModel):
    content: str
    tags: List[str] = []


class ImageUpdate(BaseModel):
    image_url: str
    content: str


class ImageResponse(BaseModel):
    id: int
    image_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: int
    tags: List[TagRequest]
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class ImageURLResponse(BaseModel):
    image_url: str
    image_transformed_url: str
    qr_code: str


class ImageSearch(BaseModel):
    id: int
    image_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: int
    tags: List[TagRequest]
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True
