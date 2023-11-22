from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.models.user import User
from src.models.image import Tag
from src.schemas.image import ImageCreate, ImageResponse, ImageUpdate, ImageURLResponse, ImageSearch
from src.schemas.tag import TagResponse
from src.repository import images as repository_images
from src.repository import search as repository_search
from src.utils.qr_code import create_qr_code_from_url
from src.utils.image_utils import (
    post_cloudinary_image,
    get_cloudinary_image_transformation,
)
from src.services.auth_service import auth_service
import logging

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/search_by_keyword/", name="Search images by keyword", response_model=List[ImageSearch])
async def search_image_by_keyword(search_by: str, filter_by: str = Query(None, enum=["rating", "created_at"]),
                                  db: Session = Depends(get_db)):
    """
    The search_image_by_keyword function searches for images by keyword.
        Args:
            search_by (str): The keyword to search for.
            filter_by (str): The field to sort the results by, either rating or created_at.

    :param search_by: str: Search for an image by keyword
    :param filter_by: str: Filter the images by rating or created_at
    :param enum: Specify the type of filter that will be applied to the search
    :param &quot;created_at&quot;]): Filter the images by date
    :param db: Session: Access the database
    :return: A list of images that match the search criteria
    :doc-author: Trelent
    """
    if search_by is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found image"
        )
    elif filter_by is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image does not have rating"
        )
    elif search_by:
        image = await repository_search.search_image_by_keyword(search_by, filter_by, db)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Images by keyword not found"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Images by keyword not found"
        )

    return image


@router.get("/search_by_tag/", name="Search images by tag", response_model=List[ImageSearch])
async def search_image_by_tag(search_by: str, filter_by: str = Query(None, enum=["rating", "created_at"]),
                              db: Session = Depends(get_db)):
    """
    The search_image_by_tag function is used to search for images by tag.
        The function takes in a string, which is the tag that you want to search for.
        It also takes in an optional filter_by parameter, which can be either &quot;rating&quot; or &quot;created_at&quot;.
        If no filter_by parameter is provided, it will default to None and return all images with the given tag.

    :param search_by: str: Search for images by tag
    :param filter_by: str: Filter the search by rating or created_at
    :param enum: Limit the possible values that can be passed to a parameter
    :param &quot;created_at&quot;]): Filter the search by date
    :param db: Session: Get the database session
    :return: A list of images with the given tag
    :doc-author: Trelent
    """
    if search_by is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found tag"
        )
    elif filter_by is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image does not have rating with this tag"
        )

    if search_by:
        image = await repository_search.search_image_by_tag(search_by, filter_by, db)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Images by tag not found"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Images by tag not found"
        )

    return image
