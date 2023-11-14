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
