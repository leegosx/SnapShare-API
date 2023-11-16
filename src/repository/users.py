from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session
from src.services.auth_service import auth_service, pickle
from src.models.user import User
from src.models.image import Image, Tag
from src.schemas.user import UserBase, Username
from src.schemas.tag import TagRequest, TagResponse

async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it returns None.

    :param email: str: Pass in the email of the user we want to retrieve from our database
    :param db: Session: Pass the database session to the function
    :return: The first user with the specified email
    """
    return db.query(User).filter(User.email == email).first()


async def count_users(db: Session) -> list:
    """
    The count_users function returns a list of all users in the database.
    
    :param db: Session: Pass in the database session
    :return: A list of all the users in the database
    """
    users = db.query(User).all()
    return users


async def create_user(body: UserBase, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        It takes a UserBase object as an argument, and returns a User object.
        The function first checks if there are any users in the database already, 
            and if not it sets the role of this user to admin. 
    
    :param body: UserBase: Pass the user data to the function
    :param db: Session: Access the database
    :return: The new user object
    """
    users_check = await count_users(db)
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Create_user: {e}")

    if len(users_check) == 0:
        user_data = body.model_dump()
        user_data["role"] = "admin"
        new_user = User(**user_data, avatar=avatar)
    else:
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
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.

    :param email: str: Get the email of the user to confirm
    :param db: Session: Pass the database session to the function
    :return: None
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
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def change_password(user: User, new_password: str, db: Session):
    """
    The change_password function takes a user object, a new password string, and
    a database session. It changes the user's password to the new one and commits
    the change to the database.
    
    :param user: User: Pass the user object to the function
    :param new_password: str: Pass in the new password that we want to set for the user
    :param db: Session: Pass the database session to the function
    :return: The user object
    """
    user.password = new_password
    db.commit()
    return user

async def get_user_by_username(username: str, db: Session) -> User:
    """
    The get_user_by_username function takes a username and returns the user object associated with that username.
    If no such user exists, it returns None.
    
    :param username: str: Specify the username of the user we want to retrieve
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    return db.query(User).filter(User.username == username).first()

async def update_user(user: User, db: Session):
    """
    The update_user function takes a user object and a database session as arguments.
    It adds the user to the database, commits it, refreshes it, and returns the updated
    user.
    
    :param user: User: Pass in the user object that is to be updated
    :param db: Session: Pass the database session to the function
    :return: The user object
    """
    db.add(user)
    db.commit()
    db.refresh(user)

    redis_key = f"user:{user.email}" 
    auth_service.redis.set(redis_key, pickle.dumps(user))
    auth_service.redis.expire(redis_key, 900)
    
    return user
    
async def get_user_images(user: User, db: Session) -> list:
    """
    The get_user_images function takes a user object and a database session as arguments.
    It returns the number of images that the user has uploaded.
    
    :param user: User: Get the user's id
    :param db: Session: Access the database
    :return: The number of images a user has uploaded
    """
    return db.query(Image).filter(Image.user_id == user.id).count()