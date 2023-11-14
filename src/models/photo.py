from sqlalchemy import Table, Column, String, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, Base

photo_m2m_tags = Table(
    "photo_m2m_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Photo(BaseModel):
    __tablename__ = "photos"

    image_url = Column(String, nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="photos")
    tags = relationship("Tag", secondary=photo_m2m_tags, back_populates="photos")


class Tag(BaseModel):
    __tablename__ = "tags"

    name = Column(String, unique=True)
    photos = relationship("Photo", secondary=photo_m2m_tags, back_populates="tags")
