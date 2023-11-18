from typing import List, Union
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.models.user import User
from src.schemas.rating import RatingRequest, RatingResponse
from src.repository import images as repository_images
from src.repository import ratings as repository_ratings
from src.services.auth_service import auth_service


router = APIRouter(prefix="/rating", tags=["rating"])

@router.get("/all", response_model=List[RatingResponse])
async def get_all_ratings(image_id: int, db: Session = Depends(get_db)):
    """
    The get_all_ratings function returns all ratings for a given image.
        The function takes an image_id as input and returns a list of rating objects.
    
    :param image_id: int: Get the image_id from the url
    :param db: Session: Pass the database session to the function
    :return: A list of ratings
    """
    images = repository_images.get_image(image_id, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    ratings = repository_ratings.get_ratings(db, image_id=image_id)
    return await ratings

@router.get("/{rating_id}", response_model=RatingResponse)
async def get_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    The get_rating function returns a rating object based on the id of the rating.
        If no such rating exists, it will return an HTTP 404 error.
    
    :param rating_id: int: Specify the rating id of the rating to be retrieved
    :param db: Session: Get the database session
    :return: A rating object
    """
    rating = repository_ratings.get_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return await rating

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    The remove_rating function removes a rating from the database.
        It takes in an integer representing the id of the rating to be removed, and returns a JSON object containing information about that rating.
    
    :param rating_id: int: Identify the rating to be removed from the database
    :param db: Session: Pass the database session to the function
    :return: The removed rating object
    """
    rating = repository_ratings.remove_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    repository_images.average_rating(rating.image_id, db)
    return await rating
    
    
@router.post("/add", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def add_rating(body: RatingRequest, image_id: int, db: Session = Depends(get_db), 
               current_user: User = Depends(auth_service.get_current_user)):
    """
    The add_rating function adds a rating to an image.
        The user must be logged in and cannot rate their own images.
        If the user has already rated the image, they will receive an error message.
    
    :param body: RatingRequest: Get the rating value from the request body
    :param image_id: int: Get the image from the database
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :return: A rating object
    """
    
    image = repository_images.get_image(image_id, db)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    existing_rating = repository_ratings.get_ratings(db, image_id=image_id, user_id=current_user.id)
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already rated this image")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot rate your own image")
    rating = repository_ratings.add_rating(body, image_id, current_user.id, db)
    repository_images.average_rating(image_id, db)
    return await rating