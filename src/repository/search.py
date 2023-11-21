from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session

from src.models.user import User
from src.models.image import Image, Tag
from src.models.rating import Rating


async def search_by_tag(tag: str, rating_low: float, rating_high: float, start_data: date, end_data: date, db: Session):
    ...


async def search_by_content(content: str, rating_low: float, rating_high: float, start_data: date, end_data: date, db: Session):
    ...

async def search_by_username(username: str, db: Session,):
    return db.query(User).filter(User.username == username).first()