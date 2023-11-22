from sqlalchemy import and_, or_, nulls_last
from sqlalchemy.orm import Session, joinedload
from typing import List

from src.models.image import Image, Tag
from src.models.rating import Rating
from src.models.user import User
from src.schemas.image import ImageCreate, ImageUpdate
from src.repository.ratings import get_ratings


async def search_image_by_keyword(search_by: str, filter_by: str, db: Session):
    """
    The search_image_by_keyword function searches for images by keyword and returns a list of Image objects.
    The function takes in three parameters: search_by, filter_by, and db. The search_by parameter is the string that will be searched for in the database.
    The filter_by parameter is either &quot;created at&quot; or &quot;rating&quot;. If it's created at, then the results are ordered by creation date (oldest to newest).
    If it's rating, then they're ordered from highest to lowest rating score.

    :param search_by: str: Search the database for a keyword
    :param filter_by: str: Filter the results by either created_at or rating
    :param db: Session: Pass the database session to the function
    :return: A list of images that match the search_by parameter
    :doc-author: Trelent
    """
    if filter_by == "created_at":
        result = db.query(Image).filter(Image.content.like(search_by)).order_by(Image.created_at).all()
    elif filter_by == "rating":
        result = (
            db.query(Image)
            .join(Image.ratings)
            .filter(Image.content.like(search_by))
            .options(joinedload(Image.ratings))
            .order_by(nulls_last(Rating.rating_score))
            .all()
        )
    return result


async def search_image_by_tag(search_by: str, filter_by: str, db: Session):

    """
    The search_image_by_tag function searches for images by tag name and returns a list of Image objects.
        The function takes in three parameters: search_by, filter_by, and db.
        The search_by parameter is the tag name to be searched for.
        The filter_by parameter is either &quot;created at&quot; or &quot;rating&quot;. If it's created at, then the results are ordered by creation date (oldest first).
            If it's rating, then the results are ordered by rating score (highest first).

    :param search_by: str: Search for the tag name
    :param filter_by: str: Filter the search results by either created_at or rating
    :param db: Session: Pass the database session to the function
    :return: A list of image objects
    :doc-author: Trelent
    """
    if filter_by == "created_at":
        result = db.query(Image).join(Image.tags).filter(Tag.name == search_by).order_by(Image.created_at).all()

    elif filter_by == "rating":
        result = (
            db.query(Image)
            .join(Image.ratings)
            .join(Image.tags)
            .filter(Tag.name == search_by)
            .options(joinedload(Image.ratings))
            .order_by(nulls_last(Rating.rating_score)).all()
        )
    return result