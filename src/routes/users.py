from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
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
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
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
