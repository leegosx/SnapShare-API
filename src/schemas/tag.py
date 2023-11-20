from pydantic import BaseModel, ConfigDict
from typing import ClassVar


class TagRequest(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    tag: str
    image_id: int
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

class TagModel(BaseModel):
    id: int
    name: str