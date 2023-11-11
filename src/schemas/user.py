from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import ClassVar


class UserBase(BaseModel):
    username: str
    email: EmailStr


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
