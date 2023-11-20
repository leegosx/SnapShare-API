from sqlalchemy import Table, Column, String, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, Base

image_m2m_tags = Table(
    "image_m2m_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(BaseModel):
    __tablename__ = "images"

    image_url = Column(String, nullable=False)
    image_transformed_url = Column(String, nullable=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ratings = relationship("Rating", back_populates="image")
    comments = relationship("Comment", back_populates="image")
    user = relationship("User", back_populates="images")
    tags = relationship("Tag", secondary=image_m2m_tags, back_populates="images")


class Tag(BaseModel):
    __tablename__ = "tags"

    name = Column(String, unique=True)
    images = relationship("Image", secondary=image_m2m_tags, back_populates="tags")
