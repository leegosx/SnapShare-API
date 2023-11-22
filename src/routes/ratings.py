from typing import List, Union
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.models.user import User, UserRole
from src.schemas.rating import RatingRequest, RatingResponse, ImageRatingsResponse, AllRatingResponse
from src.repository import images as repository_images
from src.repository import ratings as repository_ratings
from src.services.auth_service import auth_service
from src.services import roles

router = APIRouter(prefix="/rating", tags=["rating"])

@router.get("/photo/{image_id}/", response_model=List[ImageRatingsResponse], 
            dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def get_by_photo_ratings(image_id: int, db: Session = Depends(get_db)):
    """
    The get_all_ratings function returns all ratings for a given image.
        The function takes an image_id as input and returns a list of rating objects.
    
    :param image_id: int: Get the image_id from the url
    :param db: Session: Pass the database session to the function
    :return: A list of ratings
    """
    images = await repository_images.get_image(image_id, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    ratings = await repository_ratings.get_ratings(db, image_id=image_id)
    if not ratings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ratings found for this image")
    
    average_rating = sum(rating.rating_score for rating in ratings) / len(ratings) if ratings else 0.0

    rating_responses = [
        ImageRatingsResponse(
            id=rating.id,
            user_id=rating.user_id,
            image_id=rating.image_id,
            average_rating=average_rating 
        )
        for rating in ratings
    ]
    return rating_responses

@router.get("/all", response_model=List[AllRatingResponse], 
            dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def get_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    The get_ratings function returns all ratings in the database.
        The function takes no input and returns a list of rating objects.

    :param db: Session: Pass the database session to the function
    :return: A list of ratings
    """
    ratings = await repository_ratings.get_all_ratings(skip, limit, db)
    if not ratings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ratings found")
    return ratings

@router.get("/get/{rating_id}/", response_model=RatingResponse, 
            dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def get_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    The get_rating function returns a rating object based on the id of the rating.
        If no such rating exists, it will return an HTTP 404 error.
    
    :param rating_id: int: Specify the rating id of the rating to be retrieved
    :param db: Session: Get the database session
    :return: A rating object
    """
    rating =await repository_ratings.get_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating

@router.delete("/remove/{rating_id}", status_code=status.HTTP_204_NO_CONTENT, 
               dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def remove_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    The remove_rating function removes a rating from the database.
        It takes in an integer representing the id of the rating to be removed, and returns a JSON object containing information about that rating.
    
    :param rating_id: int: Identify the rating to be removed from the database
    :param db: Session: Pass the database session to the function
    :return: The removed rating object
    """
    rating = await repository_ratings.remove_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating
    
    
@router.post("/add_rating/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
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
    
    image = await repository_images.get_image(image_id, db)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    existing_rating = await repository_ratings.get_ratings(db, image_id=image_id, user_id=current_user.id)
    if len(existing_rating) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already rated this image")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot rate your own image")
    if body.rating not in range(1, 6):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5")
    rating = repository_ratings.add_rating(body, image_id, current_user.id, db)
    await repository_images.average_rating(image_id, db)
    return await rating