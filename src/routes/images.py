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

router = APIRouter(prefix="/images", tags=["images"])


@router.post(
    "/create_new", response_model=ImageResponse, status_code=status.HTTP_201_CREATED
)
async def create_image(
        file: UploadFile = File(...),
        body: ImageCreate = Depends(),
        user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
    Creates a new image for the user.

    The function first checks if the number of tags in the request does not exceed the maximum limit (5).
    It then uploads the provided image file to Cloudinary and creates a new image record in the database.

    Args:
        file (UploadFile): The image file to be uploaded.
        body (ImageCreate): Object containing image details, including tags.
        user (User): The current authenticated user.
        db (Session): Database session dependency.

    Returns:
        ImageResponse: The created image object.

    Raises:
        HTTPException: If the number of tags exceeds the limit or if the image could not be created.
    """
    # Check for the number of tags
    tag_list = body.tags[0].split(",")  # Split the string into a list
    body.tags = tag_list
    if len(body.tags) > 5:
        logging.warning(f"User {user.id} tried to upload image with too many tags.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of tags is 5",
        )

    try:
        # Upload the image to Cloudinary
        image_url = post_cloudinary_image(file, user)

        # Create the image in the database
        images = await repository_images.create_image(image_url, body, user, db)
        if images is None:
            logging.error(f"Image creation failed for user {user.id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Image not created"
            )

        return images

    except Exception as e:
        logging.error(f"Error in image creation for user {user.id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
        image_id,
        body: ImageUpdate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
    The update_image function updates an image in the database.
        Args:
            image_id (int): The id of the image to update.
            body (ImageUpdate): The updated information for the Image object.
            current_user (User = Depends(auth_service.get_current_user)): The user making this request, if any is logged in at all.  If no user is logged in, then this will be None and we'll raise a 401 Unauthorized error when we try to access it later on down below where we check that only admins can update images or that only users who own an

    :param image_id: Find the image in the database
    :param body: ImageUpdate: Pass the data that will be used to update the image
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Pass the database session to the repository
    :param : Get the image id
    :return: The updated image
    :doc-author: Trelent
    """
    image = await repository_images.update_image(image_id, body, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
        image_id: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
    The delete_image function deletes an image from the database.
        Args:
            image_id (str): The id of the image to delete.
            current_user (User): The user who is deleting the image.
            db (Session): A database session object for interacting with a PostgreSQL database.

    :param image_id: str: Get the image id from the url
    :param current_user: User: Get the user id of the currently logged in user
    :param db: Session: Get the database session
    :param : Get the image_id from the url
    :return: An image object
    :doc-author: Trelent
    """
    image = await repository_images.delete_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    # current_user.uploaded_images -= 1
    return image


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: str, db: Session = Depends(get_db)):
    """
    The get_image function returns an image object based on the image_id parameter.
    If no such image exists, it raises a 404 error.

    :param image_id: str: Get the image id from the url
    :param db: Session: Pass the database session to the function
    :return: An image object
    :doc-author: Trelent
    """
    image = await repository_images.get_image(image_id, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    return image


@router.get("/", response_model=list())
async def get_images(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
    The get_images function returns a list of images.
        ---
        get:
          summary: Get all images
          description: Returns a list of all the available images.
          tags: [images]

    :param skip: int: Skip the first n images
    :param limit: int: Limit the number of images returned
    :param current_user: User: Get the current user
    :param db: Session: Get the database session
    :param : Skip the first n images
    :return: A list of images
    :doc-author: Trelent
    """
    images = await repository_images.get_images(skip, limit, current_user, db)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Images not found"
        )
    return images


@router.patch(
    "/add_tags",
    response_model=ImageResponse,
    status_code=status.HTTP_200_OK,
    summary="Add tags to a image",
)
async def add_tag(
        body: TagResponse,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    The add_tag function adds a tag to an image.

    :param body: TagResponse: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user who is making the request
    :param : Get the image id from the body of the request
    :return: The image object
    :doc-author: Trelent
    """
    image = await repository_images.get_image_user(
        image_id=body.image_id, db=db, current_user=current_user
    )
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    if len(image.tags) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 tags are allowed per image",
        )

    tag = db.query(Tag).filter_by(name=body.tag).first()
    if not tag:
        tag = Tag(name=body.tag)
        db.add(tag)
        db.commit()

    if tag not in image.tags:
        image.tags.append(tag)
        image_data = ImageUpdate(image_url=image.image_url, content=image.content)
        await repository_images.update_image(
            image.id, image_data=image_data, current_user=current_user, db=db
        )

    return image


@router.post("/transform_image/", response_model=ImageURLResponse)
async def transform_image(
        image_url: str,
        transformation_type: str = Query(
            ...,
            description="Type of transformation: resize, crop, effect, overlay, face_detect",
        ),
        width: int = None,
        height: int = None,
        effect: str = None,
        overlay_image_url: str = None,
        db: Session = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    The transform_image function takes an image_url, transformation_type, width, height, effect and overlay_image_url as parameters.
    The function then calls the get_cloudinary_image transformation function to transform the image based on the parameters passed in.
    It then creates a QR code from that transformed url and adds it to our database using repository functions.

    :param image_url: str: Get the image url from the user
    :param transformation_type: str: Determine the type of transformation to be applied to the image
    :param description: Document the api
    :param crop: Crop the image to a specific width and height
    :param effect: Apply an effect to the image
    :param overlay: Specify the public id of an image that you want to overlay on top of your original image
    :param face_detect&quot;: Detect faces in the image and crop them out
    :param ): Crop the image to a specific width and height
    :param width: int: Set the width of the image
    :param height: int: Set the height of the image
    :param effect: str: Apply an effect to the image
    :param overlay_image_url: str: Overlay an image on top of the original image
    :param db: Session: Get the database session
    :param user: User: Get the user from the database
    :param : Determine the type of transformation to be applied on the image
    :return: A dictionary
    :doc-author: Trelent
    """
    try:
        transformed_url = get_cloudinary_image_transformation(
            user, transformation_type, width, height, effect, overlay_image_url
        )

        qr_code = create_qr_code_from_url(transformed_url)

        _ = await repository_images.add_transform_url_image(
            image_url=image_url,
            transform_url=transformed_url,
            current_user=user,
            db=db,
        )
        return {
            "image_url": image_url,
            "image_transformed_url": transformed_url,
            "qr_code": qr_code,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transformed_image/{image_id}", response_model=ImageURLResponse)
async def get_transform_image_url(
        image_id: str,
        db: Session = Depends(get_db),
):
    """
    The get_transform_image_url function returns the transformed image URL and a QR code for that URL.


    :param image_id: str: Get the image from the database
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :param : Get the image id from the url and then pass it to the function
    :return: The image_url, the transformed image url and the qr code for that transformed url
    :doc-author: Trelent
    """
    image = await repository_images.get_image(image_id, db)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    if image.image_transformed_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image was not transformed, please transform first.",
        )

    qr_code = create_qr_code_from_url(image.image_transformed_url)
    return {
        "image_url": image.image_url,
        "image_transformed_url": image.image_transformed_url,
        "qr_code": qr_code,
    }



