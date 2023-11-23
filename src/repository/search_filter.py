from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from src.models.base import Base
from typing import List, Optional

from src.models.image import Image
from src.models.rating import Rating

def get_rating_score(image_id: int, db: Session) -> Optional[float]:
    rating = (
        db.query(func.avg(Rating.rating_score))
        .filter(Rating.image_id == image_id)
        .scalar()
    )
    return round(rating, 1) if rating is not None else None


def get_images_by_search(
    db: Session,
    tag: str,
    keyword: str,
    min_rating: int,
    max_rating: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[Image]:
    images_query = db.query(Image)

    # Apply search based on the query
    if tag:
        images_query = images_query.filter(Image.tags.any(name=tag))
    if keyword:
        images_query = images_query.filter(Image.content.ilike(f"%{keyword}%"))

    # Apply filters
    if min_rating is not None:
        images_query = images_query.filter(Image.ratings.any(Rating.rating_score >= min_rating))

    if max_rating is not None:
        images_query = images_query.filter(Image.ratings.any(Rating.rating_score <= max_rating))
        
    if start_date is not None:
        images_query = images_query.filter(Image.created_at >= start_date)

    if end_date is not None:
        images_query = images_query.filter(Image.created_at <= end_date)

    images = images_query.all()
    for image in images:
        image.average_rating = get_rating_score(image.id, db)
    return images
