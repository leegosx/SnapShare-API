from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from src.models.base import Base
from src.models.user import User
from src.models.image import Image
from src.models.rating import Rating
from src.schemas.user import UserSearchResponse

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


async def get_images_by_user(
    db: Session,
    user_id: int,
    min_rating: int = 0,
    max_rating: int = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Image]:
    """
    The get_images_by_user function returns a list of images that are associated with the user_id passed in.
        The function also takes optional parameters to filter the results by rating and date range.
    
    :param db: Session: Connect to the database
    :param user_id: int: Filter the images by user_id
    :param min_rating: int: Filter out images that have a rating score less than the min_rating
    :param max_rating: int: Set the maximum rating score for an image
    :param start_date: Optional[str]: Filter the images by a start date
    :param end_date: Optional[str]: Filter the images by their created_at date
    :return: A list of usersearchresponse objects
    """
    query = db.query(Image).filter(Image.user_id == user_id)
    if min_rating is not None or max_rating is not None:
        query = query.join(Rating, isouter=True).group_by(Image.id)
        if min_rating is not None:
            query = query.having(func.coalesce(func.avg(Rating.rating_score), 0) >= min_rating)
        if max_rating is not None:
            query = query.having(func.coalesce(func.avg(Rating.rating_score), 0) <= max_rating)

    if start_date is not None:
        query = query.filter(Image.created_at >= start_date)

    if end_date is not None:
        query = query.filter(Image.created_at <= end_date)

    images = query.all()
    result_list = []
    for image in images:
        result = UserSearchResponse(
            id=image.id,
            image_url=image.image_url,
            username=image.user.username,
            created_at=image.created_at,
            updated_at=image.updated_at,
            user_id=image.user_id,
            content=image.content,
            average_rating=await get_rating_score(image.id, db)
        )
        result_list.append(result)

    return result_list
