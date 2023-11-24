from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from src.models.base import Base
from typing import Optional, List
from datetime import datetime

from src.database.db import get_db
from src.models.user import User
from src.schemas.image import ImageSearch
from src.schemas.user import UserSearchResponse
from src.repository import search_filter as repository_search_filter
from src.services import roles

router = APIRouter(prefix="/search_filter", tags=["search_filter"])

@router.get("/search/", response_model=List[ImageSearch])
async def search_images(
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    min_rating: int = Query(0, description="Minimum rating"),
    max_rating: int = Query(5, description="Maximum rating"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    The search_images function searches for images based on the provided parameters.
        The tag parameter is used to search for images with a specific tag.
        The keyword parameter is used to search for images with a specific keyword in their description or title.
        The min_rating and max_rating parameters are used to filter out any image that does not have a rating between these two values (inclusive). 
            If no value is provided, the default value of 0 will be assumed as the minimum rating, and 5 will be assumed as the maximum rating. 
    
    :param tag: Optional[str]: Specify that the tag parameter is optional
    :param keyword: Optional[str]: Filter images by keyword
    :param min_rating: int: Specify the minimum rating of images to be returned
    :param description: Specify the description of the endpoint
    :param max_rating: int: Specify the maximum rating that can be returned
    :param description: Provide a description for the endpoint in the openapi documentation
    :param start_date: Optional[str]: Filter the images based on the date they were uploaded
    :param end_date: Optional[str]: Specify the end date for the search
    :param db: Session: Pass the database session to the function
    :param : Get the image id from the path
    :return: A list of images
    """
    # Perform the search based on the query and filter parameters
    if tag is None and keyword is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one of tag or keyword must be provided")

    images = await repository_search_filter.get_images_by_search(db, tag, keyword, min_rating, max_rating, start_date, end_date)
    
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No images with rating found")
    
    return images

@router.get("/search/{user_id}/images", response_model=List[UserSearchResponse],
            dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def search_images_by_user(
    user_id: int,
    min_rating: int = Query(0, description="Minimum rating"),
    max_rating: int = Query(5, description="Maximum rating"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    The search_images_by_user function searches for images by a user.
    
    :param user_id: int: Specify the user id of the user whose images are to be searched
    :param min_rating: int: Set the minimum rating of an image
    :param description: Describe the parameter in the swagger documentation
    :param max_rating: int: Set the maximum rating that can be returned
    :param description: Describe the parameter in the swagger documentation
    :param start_date: Optional[str]: Specify that the start_date parameter is optional
    :param end_date: Optional[str]: Specify that the end_date parameter is optional
    :param db: Session: Get the database session
    :return: A list of images
    """
    user_exists = user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id {user_id} not found."
        )
    return await repository_search_filter.get_images_by_user(db, user_id, min_rating, max_rating, start_date, end_date)