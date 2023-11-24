from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import ClassVar


class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str
    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailSchema(BaseModel):
    email: EmailStr


class ResetPasswordModel(BaseModel):
    email: EmailStr
    reset_password_token: str
    password: str
    confirm_password: str
    
class UserProfile(BaseModel):
    id: int
    username: str
    uploaded_images: Optional[int]
    avatar: str
    
class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    uploaded_images: Optional[int]
    avatar: str
    role: str
    
class UserUpdateAvatar(BaseModel):
    username: str
    avatar: str
    detail: str = "Avatar successfully changed!"

class Username(BaseModel):
    username: str
    
class UsernameResonpose(BaseModel):
    username: str
    detail: str = "Username successfully changed!"
    
class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    
class UserSearchResponse(BaseModel):
    id: int
    image_url: str
    username: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: int
    content: str
    average_rating: Optional[float] = None