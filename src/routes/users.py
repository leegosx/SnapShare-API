from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.models.user import User
from src.schemas.user import UserDb, UserInfo, UserProfile, Username, UsernameResonpose, UserUpdateAvatar
from src.repository import users as repository_users
from src.services.auth_service import auth_service
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserInfo)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The read_users_me function returns the current user's information.
        ---
        get:
          tags: [users] # This is a tag that can be used to group operations by resources or any other qualifier.
          summary: Returns the current user's information.
          description: Returns the current user's information based on their JWT token in their request header.
          responses: # The possible responses this operation can return, along with descriptions and examples of each response type (if applicable).
            &quot;200&quot;:  # HTTP status code 200 indicates success! In this case, it means we successfully returned a User

    :param current_user: User: Get the current user from the database
    :return: The current user object
    """
    uploaded_images_count = await repository_users.get_user_images(current_user, db)
    user_me_info_response = UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        uploaded_images=uploaded_images_count,
        avatar=current_user.avatar,
        role=current_user.role,
    )
    return user_me_info_response


@router.patch("/avatar", response_model=UserUpdateAvatar)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_avatar_user function updates the avatar of a user.
        Args:
            file (UploadFile): The image to be uploaded as an avatar.
            current_user (User): The user whose avatar is being updated.
            db (Session): A database session object for interacting with the database.

    :param file: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: The user object with the new avatar_url, but i want to return only the avatar_url
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    public_id = f"SnapShare-API/{current_user.username}{current_user.id}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id, owerwrite=True)
    avatar_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(current_user.email, avatar_url, db)

    return user


@router.get(
    "/profile/{username}", response_model=UserProfile, status_code=status.HTTP_200_OK
)
async def get_user_profile(username: str, db: Session = Depends(get_db)):
    """
    The get_user_profile function returns the user profile of a given username.

    :param username: str: Specify the username of the user whose profile we want to get
    :param db: Session: Pass the database session to the function
    :return: A userprofile object
    """
    user = await repository_users.get_user_by_username(username=username, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    uploaded_images_count = await repository_users.get_user_images(user, db)

    user_profile_response = UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        uploaded_images=uploaded_images_count,
        avatar=user.avatar,
    )

    return user_profile_response


@router.patch(
    "/change/{username}",
    response_model=UsernameResonpose,
    status_code=status.HTTP_200_OK,
)
async def change_username(
    body: Username,
    user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The change_username function takes in a Username object and returns a User object.
    The Username object contains the new username that will be assigned to the user.
    The User object is returned with its username field updated.

    :param body: Username: Get the new username from the request body
    :param user: User: Get the current user from the database
    :param db: Session: Access the database
    :return: The updated user
    """
    if body.username == user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be the same as the current username",
        )
    exists_username = await repository_users.get_user_by_username(
        username=body.username, db=db
    )
    if exists_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    user.username = body.username
    user = await repository_users.update_user(auth_service.redis ,user, db)
    return user

@router.patch('/ban_user')
async def ban_user(email: str, db: Session = Depends(get_db)):
    """
    The ban_user function is used to ban a user by email.
        The function takes an email as input and returns the banned user's details.
    :param email: str: Get the email of a user from the request body
    :param db: Session: Get the database session
    :return: A dictionary with the user and detail
    """
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such user is not found",
        )
    user = await repository_users.to_ban_user(user, email, db)
    return {"detail": "User was banned"}