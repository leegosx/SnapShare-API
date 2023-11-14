import enum

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

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
    role = Column(String, default="user")
    images = relationship("Image", back_populates="user")
    refresh_token = Column(String, nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
