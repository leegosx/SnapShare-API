from pydantic import BaseModel, ConfigDict
from typing import ClassVar


class Tag(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    tag: str
    image_id: int
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
