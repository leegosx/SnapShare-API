from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, ClassVar


class CommentRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: Optional[int] = None
    photo_id: int
    user_id: int
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
