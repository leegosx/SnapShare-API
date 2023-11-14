from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import UserBase


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it returns None.
    
    :param email: str: Pass in the email of the user we want to retrieve from our database
    :param db: Session: Pass the database session to the function
    :return: The first user with the specified email
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserBase, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserBase): The UserBase object to be created.
            db (Session): The SQLAlchemy session object used for querying the database.
        Returns:
            User: A newly created user from the database.
    
    :param body: UserBase: Pass the data from the request body into this function
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Create_user: {e}")
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: UserBase, token: Union[str, None], db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.
    
    :param user: UserBase: Identify the user in the database
    :param token: Union[str: Pass the token to the function
    :param None]: Indicate that the function can accept either a string or none
    :param db: Session: Commit the changes to the database
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Get the email of the user to confirm
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    Args:
        email (str): The email address of the user to update.
        url (str): The URL for the new avatar image.
        db (Session, optional): A database session object to use instead of creating one locally. Defaults to None.  # noQA: E501 line too long; pylint: disable=line-too-long  # noQA: E501 line too long; pylint: disable=line-too-long  # noQA: E501 line too long;
    
    :param email: Get the user from the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass in the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
