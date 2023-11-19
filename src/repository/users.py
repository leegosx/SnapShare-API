from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.models.blacklist import Blacklist
from src.models.user import User
from src.schemas.user import UserBase
from src.services.auth_service import auth_service


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists, it returns None.

    :param email: str: Specify the type of the parameter
    :param db: Session: Pass a database session to the function
    :return: A user object if the email exists in the database
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def count_users(db: Session) -> list:
    """
    The count_users function returns a list of all users in the database.

    :param db: Session: Pass the database session to the function
    :return: A list of all the users in the database
    :doc-author: Trelent
    """
    users = db.query(User).all()
    return users


async def create_user(body: UserBase, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserBase): The UserBase object to be created.
            db (Session): The SQLAlchemy session object used for querying the database.

    :param body: UserBase: Create a new user
    :param db: Session: Pass the database session to the function
    :return: The newly created user object
    :doc-author: Trelent
    """
    users_check = await count_users(db)
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Create_user: {e}")

    if len(users_check) == 0:
        user_data = body.dict()
        user_data["role"] = "admin"
        new_user = User(**user_data, avatar=avatar)
    else:
        new_user = User(**body.dict(), avatar=avatar)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: UserBase, token: Union[str, None], db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: UserBase: Identify the user in the database
    :param token: Union[str: Specify that the token can be a string or none
    :param None]: Specify that the token parameter can be either a string or none
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email of the user to be confirmed
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

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed in
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def change_password(user: User, new_password: str, db: Session):
    """
    The change_password function takes a user object, a new password string, and the database session.
    It then changes the user's password to the new one and commits it to the database.

    :param user: User: Specify the type of object that is passed in
    :param new_password: str: Pass in the new password that the user wants to use
    :param db: Session: Access the database
    :return: The user object
    :doc-author: Trelent
    """
    user.password = new_password
    db.commit()
    return user


async def save_black_list_token(token: str, current_user: auth_service.get_current_user, db):
    """
    The save_black_list_token function saves a token to the blacklist.
        Args:
            token (str): The JWT auth_token that is being saved to the blacklist.
            current_user (User): The user who's token is being saved to the blacklist.

    :param token: str: Pass the token that is being blacklisted
    :param current_user: auth_service.get_current_user: Get the current user
    :param db: Access the database
    :return: The token that was saved
    :doc-author: Trelent
    """
    blacklist_token = Blacklist(token=token, email=current_user.email)
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
    :doc-author: Trelent
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
    :doc-author: Trelent
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
    :doc-author: Trelent
    """
    user = db.query(User).filter_by(email=username).first()
    return user.ban_status
