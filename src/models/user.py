import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from src.models.base import BaseModel

class UserRole(str, enum.Enum):
    Admin = "admin"
    Moderator = "moderator"
    User = "user"

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    role = Column(String, default='user')
    refresh_token = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)