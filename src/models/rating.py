from sqlalchemy import Integer,ForeignKey, Column
from sqlalchemy.orm import relationship

from src.database.db import engine
from src.models.base import BaseModel
from src.models.user import User
from src.models.image import Image

class Rating(BaseModel):
    __tablename__ = "ratings"

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    rating_score = Column(Integer, nullable=False)
    
    user = relationship('User', back_populates='ratings')
    image = relationship('Image', back_populates='ratings')
    