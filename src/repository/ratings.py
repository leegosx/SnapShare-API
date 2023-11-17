from typing import List

from sqlalchemy.orm import Session

from src.models.rating import Rating
from src.schemas.rating import RatingRequest

async def get_ratings(image_id: int, user_id: int, db: Session) -> List[Rating]:
    """
    The get_ratings function returns a list of ratings from the database.
        If an image_id is provided, it will return all ratings for that image.
        If a user_id is provided, it will return all ratings for that user.
        If both are provided, it will only return the rating(s) where both match.
    
    :param image_id: int: Filter the ratings by image_id
    :param user_id: int: Filter the ratings by user_id
    :param db: Session: Pass the database session into this function
    :return: A list of rating objects
    """
    if image_id and user_id:
        ratings = db.query(Rating).filter(Rating.image_id == image_id, Rating.user_id == user_id).all()
    elif image_id and not user_id:
        ratings = db.query(Rating).filter(Rating.image_id == image_id).all()
    elif user_id and not image_id:
        ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    else:
        ratings = db.query(Rating).all()

    return ratings

async def get_rating(rating_id: int, db: Session) -> Rating:
    """
    The get_rating function returns a rating object from the database.
        
    
    :param rating_id: int: Specify the id of the rating you want to get
    :param db: Session: Pass the database session to the function
    :return: A rating object
    """
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    return rating


async def add_rating(body: RatingRequest, image_id: int, user_id: int, db: Session) -> Rating:
    """
    The add_rating function adds a rating to the database.
        It takes in a RatingRequest object, an image_id, and user_id as parameters.
        The function then creates a new Rating object with the given parameters and adds it to the database.
    
    :param body: RatingRequest: Get the rating from the request body
    :param image_id: int: Identify the image that is being rated
    :param user_id: int: Get the user id of the user that is rating an image
    :param db: Session: Access the database
    :return: A rating object
    """
    rating = Rating(rating=body.rating, user_id=user_id, image_id=image_id)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

async def remove_rating(rating_id: int, db: Session) -> Rating:
    """
    The remove_rating function removes a rating from the database.
    :param rating_id: int: Identify the rating that is to be removed
    :param db: Session: Pass in the database session to use for this function
    :return: The rating that was removed
    """
    rating_to_remove = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating_to_remove:
        db.delete(rating_to_remove)
        db.commit()
    return rating_to_remove