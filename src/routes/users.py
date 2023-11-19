from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.models.user import User
from src.schemas.user import UserBase, UserResponse, TokenModel, UserDb
from src.repository import users as repository_users
from src.services.auth_service import auth_service
from src.conf.config import settings

router = APIRouter(prefix='/users', tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        It requires authentication, and it uses the auth_service to get the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    :doc-author: Trelent
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.
        The function takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
        It also takes in a User object, which is obtained from auth_service.get_current_user(). This ensures that only
        authenticated users can access this endpoint and change their own avatar (and not anyone else's). Finally, it
        takes in a Session object for database access.

    :param file: UploadFile: Upload the image to cloudinary
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: The updated user
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_id = f"SnapShare-API/{current_user.username}{current_user.id}"
    cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    avatar_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill',
                                                                 version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, avatar_url, db)
    return user


@router.patch('/ban_user')
async def ban_user(email: str = Form(), db: Session = Depends(get_db)):
    """
    The ban_user function is used to ban a user by email.
        The function takes an email as input and returns the banned user's details.

    :param email: str: Get the email of a user from the request body
    :param db: Session: Get the database session
    :return: A dictionary with the user and detail
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such user is not found",
        )
    user = await repository_users.to_ban_user(user, email, db)
    return {"user": user, "detail": "User was banned"}
