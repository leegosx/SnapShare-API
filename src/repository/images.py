
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.models.image import Image, Tag
from src.models.user import User
from src.schemas.image import ImageCreate, ImageUpdate
from src.repository.ratings import get_ratings

async def create_image(image_data: ImageCreate, current_user: User, db: Session):
    """
    The create_image function creates a new image in the database.
        Args:
            image_data (ImageCreate): The data to create an Image with.
            current_user (User): The user who is creating the Image.
            db (Session): A connection to the database for querying and committing changes.
        Returns:
            An instance of an Image that was created.

    :param image_data: ImageCreate: Create an imagecreate object from the request body
    :param current_user: User: Get the current user's id
    :param db: Session: Create a connection to the database
    :return: A new image object
    :doc-author: Trelent
    """
    image_dump = image_data.model_dump()
    list_tags = db.query(Tag).filter(Tag.name.in_(image_dump["tags"])).all()
    if len(list_tags) == 0:
        list_tags = [Tag(name=i) for i in image_dump["tags"]]
    new_image = Image(
        image_url=image_dump["image_url"],
        content=image_dump["content"],
        user_id=current_user['id'],
    )
    new_image.tags = list_tags
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


async def update_image(
    image_id, image_data: ImageUpdate, current_user: User, db: Session
):
    """
    The update_image function updates an image in the database.
        Args:
            image_id (int): The id of the image to update.
            current_user (User): The user who is making this request.  This is used for authorization purposes, and must be passed as a header with key 'Authorization' and value 'Bearer &lt;token&gt;'.  See README for more details on how to obtain a token.
            db (Session): A connection to the database that will be used by SQLAlchemy's ORM methods

    :param image_id: Identify the image to be updated
    :param image_data: ImageUpdate: Pass in the data that will be used to update the image
    :param current_user: User: Compare the user_id with the current_user
    :param db: Session: Create a database session
    :return: An image
    :doc-author: Trelent
    """
    # Compare user_id with current_user.id
    image = (
        db.query(Image)
        .filter(
            and_(
                Image.id == image_id,
                Image.user_id == current_user["id"],
            )
        )
        .first()
    )
    if image:
        for var, value in vars(image_data).items():
            setattr(image, var, value) if value else None
        db.add(image)
        db.commit()
        db.refresh(image)
    return image


async def delete_image(image_id: int, current_user: User, db: Session):
    """
    The delete_image function deletes an image from the database.
        Args:
            image_id (int): The id of the image to delete.
            current_user (User): The user who is deleting the image.
            db (Session): A connection to a database session for querying and committing changes.

    :param image_id: int: Identify the image to be deleted
    :param current_user: User: Get the user id from the current_user object
    :param db: Session: Access the database
    :return: The deleted image
    :doc-author: Trelent
    """
    db_image = (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == current_user["id"]))
        .first()
    )
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image


async def get_image(image_id: int, db: Session):
    """
    The get_image function returns an image object from the database.
        Args:
            image_id (int): The id of the desired image.
            db (Session): A connection to a database session.
        Returns:
            Image: An Image object containing information about the requested image.

    :param image_id: int: Filter the image by id
    :param db: Session: Pass the database session to the function
    :return: An image object
    :doc-author: Trelent
    """
    return db.query(Image).filter(and_(Image.id == image_id)).first()


async def get_images(skip: int, limit: int, current_user: User, db: Session):
    """
    The get_images function returns a list of images for the current user.

    :param skip: int: Skip the first n images
    :param limit: int: Limit the number of images returned
    :param current_user: User: Get the current user's id
    :param db: Session: Pass the database session to the function
    :return: A list of image objects
    :doc-author: Trelent
    """
    return (
        db.query(Image)
        .filter(Image.user_id == current_user["id"])
        .offset(skip)
        .limit(limit)
        .all()
    )


async def get_image_user(image_id: int, db: Session, current_user: User):
    """
    The get_image_user function returns the image with the given id if it exists and is owned by the current user.
        Args:
            image_id (int): The id of an Image object.
            db (Session): A database session to query for images.
            current_user (User): The currently logged in user, used to check ownership of an image.
    
    :param image_id: int: Get the image id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: An image object
    :doc-author: Trelent
    """
    return (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == current_user["id"]))
        .first()
    )
    
    
async def average_rating(image_id: int, db: Session):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        ratings = get_ratings(db, image_id=image_id)
        rating_avg = 0
        if len(ratings):
            n_ratings = [r.rating for r in ratings]
            rating_avg = float(sum(n_ratings)) / len(n_ratings)
        image.rating = rating_avg
        db.commit()
        db.refresh(image)
    return await rating_avg