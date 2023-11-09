from sqlalchemy.orm import Session
from sqlalchemy.future import select
from src.models.photo import Photo
from src.schemas.photo import PhotoCreate, PhotoUpdate


async def create_photo(photo_data: PhotoCreate, current_user, db: Session):
    """
    The create_photo function creates a new photo in the database.
        
    
    :param photo_data: PhotoCreate: Pass the data from the request body to create a new photo
    :param current_user: Get the user id of the current user
    :param db: Session: Access the database
    :return: A new photo object
    :doc-author: Trelent
    """
    new_photo = Photo(**photo_data.model_dump(), user_id=current_user.id)
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    return new_photo


async def update_photo(
    photo_id: int, photo_data: PhotoUpdate, current_user, db: Session
):
    """
    The update_photo function updates a photo in the database.
        Args:
            photo_id (int): The id of the photo to update.
            photo_data (PhotoUpdate): The data to update on the Photo object.
            current_user: The user who is making this request, used for authorization purposes.
            db (Session): A connection to our database, used for querying and updating records.
    
    :param photo_id: int: Identify which photo to update
    :param photo_data: PhotoUpdate: Pass in the data that will be used to update the photo
    :param current_user: Check if the user is authorized to update a photo
    :param db: Session: Pass the database session to the function
    :return: The updated photo
    :doc-author: Trelent
    """
    query = select(Photo).filter_by(id=photo_id, user_id=current_user.id)
    result = await db.execute(query)
    photo = result.scalars().first()
    if photo:
        for var, value in vars(photo_data).items():
            setattr(photo, var, value) if value is not None else None
        photo.upd
        await db.commit()
        await db.refresh(photo)
        return photo
    return None


async def delete_photo(photo_id: int, current_user, db: Session):
    """
    The delete_photo function deletes a photo from the database.
        Args:
            photo_id (int): The id of the photo to delete.
            current_user (User): The user who is deleting the photo.
            db (Session): A connection to our database session, used for querying and committing changes.
    
    :param photo_id: int: Get the photo with that id from the database
    :param current_user: Check if the user is authorized to delete the photo
    :param db: Session: Pass the database session to the function
    :return: A photo object
    :doc-author: Trelent
    """
    query = select(Photo).filter_by(id=photo_id, user_id=current_user.id)
    result = await db.execute(query)
    photo = result.scalars().first()
    if photo:
        await db.delete(photo)
        await db.commit()
        return photo
    return None


async def get_photo(photo_id: int, db: Session):
    """
    The get_photo function returns a photo object from the database.
        Args:
            photo_id (int): The id of the photo to be returned.
            db (Session): A connection to the database.
        Returns:
            Photo: The requested Photo object.
    
    :param photo_id: int: Filter the query by id
    :param db: Session: Pass the database session to the function
    :return: A single photo
    :doc-author: Trelent
    """
    query = select(Photo).filter_by(id=photo_id)
    result = await db.execute(query)
    photo = result.scalars().first()
    return photo


async def get_photos(current_user, db: Session):
    """
    The get_photos function returns a list of photos for the current user.
        Args:
            current_user (User): The currently logged in user.
            db (Session): A database session object to execute queries against.
        Returns:
            List[Photo]: A list of Photo objects that belong to the current user.
    
    :param current_user: Get the photos of a specific user
    :param db: Session: Pass in the database session object
    :return: A list of photos
    :doc-author: Trelent
    """
    query = select(Photo).filter_by(user_id=current_user.id)
    result = await db.execute(query)
    photos = result.scalars().all()
    return photos
