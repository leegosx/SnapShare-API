from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class CommentRequest(BaseModel):
    content: str
    
    
class CommentResponse(BaseModel):
    comment_id: Optional[int] = None
    photo_id: int
    user_id: int
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        form_attributes = True