from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.models.blacklist import Blacklist
from src.models.user import User
from src.models.image import Image
from src.schemas.user import UserBase
import pickle


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
    The create_user function takes a UserBase object and creates a new user in the database.
        If there are no users in the database, it will create an admin user. Otherwise, it will create
        a regular user.
    
    :param body: UserBase: Pass in the user data from the request
    :param db: Session: Access the database
    :return: A user object
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


async def update_user(redis, user: User, db: Session):
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
    redis.set(redis_key, pickle.dumps(user))
    redis.expire(redis_key, 900)

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


async def save_black_list_token(token: str, user: User, db):
    """
    The save_black_list_token function saves a token to the blacklist.
        Args:
            token (str): The JWT auth_token that is being saved to the blacklist.
            current_user (User): The user who's token is being saved to the blacklist.

    :param token: str: Pass the token that is being blacklisted
    :param current_user: auth_service.get_current_user: Get the current user
    :param db: Access the database
    :return: The token that was saved
    """
    blacklist_token = Blacklist(token=token, email=user.email)
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)


async def find_black_list_token(token: str, db: Session):
    """
    The find_black_list_token function takes in a token and a database session,
    and returns the first Blacklist object that matches the given token.


    :param token: str: Pass in the token that is being checked
    :param db: Session: Pass the database session to this function
    :return: A blacklist object if the token is in the blacklist
    """
    return db.query(Blacklist).filter(Blacklist.token == token).first()


async def to_ban_user(body: UserBase, email: str, db: Session):
    """
    The to_ban_user function takes in a user's email and sets their ban status to True.
        Args:
            body (UserBase): The UserBase object containing the user's information.
            email (str): The user's email address.

    :param body: UserBase: Get the data from the request body
    :param email: str: Specify the email of the user that is to be banned
    :param db: Session: Create a connection to the database
    :return: A user object
    """
    user = db.query(User).filter_by(email=email).first()
    user.ban_status = True
    db.commit()
    return user


async def check_ban_status(username: str, db: Session):
    """
    The check_ban_status function takes in a username and database session,
    and returns the ban status of that user. If the user is not found, it will return None.

    :param username: str: Pass in the username of the user that is trying to log in
    :param db: Session: Access the database
    :return: A boolean value that indicates whether or not the user is banned
    """
    user = db.query(User).filter_by(email=username).first()
    return user.ban_status
