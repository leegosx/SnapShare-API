from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from src.models.base import Base
from typing import List, Optional

from src.models.image import Image
from src.models.rating import Rating

async def get_rating_score(image_id: int, db: Session) -> Optional[float]:
    """
    The get_rating_score function takes in an image_id and a database session,
    and returns the average rating score for that image. If there are no ratings
    for the given image, it returns None.
    
    :param image_id: int: Specify the image id of the image to be rated
    :param db: Session: Pass in the database session to the function
    :return: A float or none
    """
    rating = (
        db.query(func.avg(Rating.rating_score))
        .filter(Rating.image_id == image_id)
        .scalar()
    )
    return round(rating, 1) if rating is not None else None


async def get_images_by_search(
    db: Session,
    tag: str,
    keyword: str,
    min_rating: int,
    max_rating: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[Image]:
    """
    The get_images_by_search function takes in a database session, tag, keyword, min_rating, max_rating and start/end dates.
    It then queries the database for images that match the search criteria. It returns a list of Image objects.
    
    :param db: Session: Pass in the database session
    :param tag: str: Filter the images by tag
    :param keyword: str: Search for a keyword in the image content
    :param min_rating: int: Filter images by the minimum rating score
    :param max_rating: int: Filter the images by their rating score
    :param start_date: Optional[str]: Filter images by the date they were created
    :param end_date: Optional[str]: Filter images based on the date they were created
    :param : Filter the images by tag
    :return: A list of images that match the search criteria
    """
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
        image.average_rating = await get_rating_score(image.id, db)
    return images
