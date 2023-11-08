from sqlalchemy import Column, Integer, String, func, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Comment(BaseModel):
    __tablename__ = "comments"
    
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    photo_id = Column(Integer, ForeignKey('photos.id'), nullable=False)
    user = relationship('User', back_populates='comments')
    photo = relationship("Photo", back_populates="comments")