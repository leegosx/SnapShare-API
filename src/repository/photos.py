from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.photo import Photo, Tag
from src.schemas.photo import PhotoCreate, PhotoUpdate


async def create_photo(photo_data: PhotoCreate, current_user, db: Session):
    """
    The create_photo function creates a new photo in the database.
        Args:
            photo_data (PhotoCreate): The data to create a new Photo object with.
            current_user (User): The user who is creating the Photo object.
            db (Session): A connection to the database, used for querying and committing changes.

    :param photo_data: PhotoCreate: Create a new photo object
    :param current_user: Get the user_id of the current user
    :param db: Session: Pass the database session to the function
    :return: A new_photo object
    :doc-author: Trelent
    """
    photo_dump = photo_data.model_dump()
    list_tags = db.query(Tag).filter(Tag.name.in_(photo_dump["tags"])).all()
    if len(list_tags) == 0:
        list_tags = [Tag(name=i) for i in photo_dump["tags"]]
    new_photo = Photo(
        image_url=photo_dump["image_url"],
        content=photo_dump["content"],
        user_id=current_user.id,
    )
    new_photo.tags = list_tags
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo


async def update_photo(
    photo_id: int, photo_data: PhotoUpdate, current_user, db: Session
):
    """
    The update_photo function updates a photo in the database.
        Args:
            photo_id (int): The id of the photo to update.
            photo_data (PhotoUpdate): The data to update for the given Photo object.
                This is a Pydantic model, so it will be validated before being passed into this function.
            current_user: A FastAPI dependency that contains information about who is currently logged in and making this request.
                It's used here to ensure that only users can edit their own photos, not other people's photos!

    :param photo_id: int: Find the photo in the database
    :param photo_data: PhotoUpdate: Pass in the data from the request body
    :param current_user: Check if the user is authorized to update the photo
    :param db: Session: Pass the database session to the function
    :return: The updated photo
    :doc-author: Trelent
    """
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user == current_user)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    for var, value in vars(photo_data).items():
        setattr(photo, var, value) if value else None

    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

async def delete_photo(photo_id: int, current_user, db: Session):
    """
    The delete_photo function deletes a photo from the database.
        Args:
            photo_id (int): The id of the photo to be deleted.
            current_user (str): The username of the user who is deleting this photo.
            db (Session): A connection to our database, used for querying and committing changes.

    :param photo_id: int: Identify the photo to be deleted
    :param current_user: Check if the user is authorized to delete the photo
    :param db: Session: Pass the database session to the function
    :return: A photo object
    :doc-author: Trelent
    """
    db_photo = (
        db.query(Photo)
        .filter(and_(Photo.id == photo_id, Photo.user_id == current_user))
        .first()
    )
    if db_photo:
        db.delete(db_photo)
        db.commit()
    return db_photo


async def get_photo(photo_id: int, db: Session):
    """
    The get_photo function returns a photo object from the database.
        Args:
            photo_id (int): The id of the photo to be returned.
            db (Session): A connection to the database.
        Returns:
            Photo: The requested Photo object.

    :param photo_id: int: Specify the id of the photo to be retrieved
    :param db: Session: Pass the database session into the function
    :return: A photo object
    :doc-author: Trelent
    """
    return db.query(Photo).filter(and_(Photo.id == photo_id)).first()


async def get_photos(skip: int, limit: int, current_user, db: Session):
    """
    The get_photos function returns a list of photos from the database.
            
        
        
    
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param current_user: Get the photos of a specific user
    :param db: Session: Pass the database session to the function
    :return: A list of photos from the database
    :doc-author: Trelent
    """
    """
    The get_photos function returns a list of photos from the database.
        
    
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param current_user: Get the photos of a specific user
    :param db: Session: Pass the database session to the function
    :return: A list of photo objects
    :doc-author: Trelent
    """
    return db.query(Photo).filter(
        Photo.user_id == current_user.offset(skip).limit(limit).all())

async def get_photo_user(photo_id: int, db: Session, current_user):
    return await db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user == current_user)).first()
