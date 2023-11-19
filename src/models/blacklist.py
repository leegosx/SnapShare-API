from sqlalchemy import Column, String


from src.models.base import BaseModel


class Blacklist(BaseModel):
    __tablename__ = "blacklists"

    token = Column(String, unique=True)
    email = Column(String, nullable=False)
