from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.models.user import User
from src.models.photo import Photo, Tag
from src.schemas.photo import PhotoBase, PhotoCreate, PhotoResponse, PhotoUpdate
from src.schemas.tag import TagResponse
from src.repository import photos as repository_photos
from src.services.auth_service import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post(
    "/create_new", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED
)
async def create_photo(
    body: PhotoCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The create_photo function creates a new photo in the database.
        The function takes a PhotoCreate object as input, which contains all of the information needed to create a new photo.
        The current_user is passed into this function by FastAPI's Depends() decorator, and it represents the user who is currently logged in and making this request.
        Finally, we pass in our database session using FastAPI's Depends() decorator.
    
    :param body: PhotoCreate: Get the data from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Pass the database connection to the repository layer
    :param : Get the current user from the database
    :return: A photo object
    :doc-author: Trelent
    """
    return await repository_photos.create_photo(body, current_user, db)


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id,
    body: PhotoUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_photo function updates a photo in the database.
        Args:
            photo_id (int): The id of the photo to update.
            body (PhotoUpdate): The updated information for the Photo object.
            current_user (User = Depends(auth_service.get_current_user)): The user making this request, if any is logged in at all.
                If no user is logged in, then current_user will be None and an HTTPException will be raised with status code 401 Unauthorized 
                because only users who are logged into their account can update photos
    
    :param photo_id: Identify the photo to be updated
    :param body: PhotoUpdate: Pass the data from the request body to the update_photo function
    :param current_user: User: Get the current user
    :param db: Session: Get the database session
    :param : Get the photo id
    :return: A photo object
    :doc-author: Trelent
    """
    photo = await repository_photos.update_photo(photo_id, body, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The delete_photo function deletes a photo from the database.
        The function takes in a photo_id and current_user as parameters,
        and returns the deleted photo.
    
    :param photo_id: str: Get the photo id of the photo to be deleted
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :param : Get the current user
    :return: A photo object
    :doc-author: Trelent
    """
    photo = await repository_photos.delete_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/{image_id}", response_model=PhotoResponse)
async def get_photo(image_id: str, db: Session = Depends(get_db)):
    """
    The get_photo function returns a photo object based on the image_id parameter.
    If no photo is found, it raises an HTTPException with status code 404 and detail message &quot;Photo not found&quot;.
    
    
    :param image_id: str: Specify the image id of the photo you want to retrieve
    :param db: Session: Get the database session from the dependency
    :return: A photo object
    :doc-author: Trelent
    """
    photo = await repository_photos.get_photo(image_id, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/", response_model=list())
async def get_photos(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The get_photos function returns a list of photos.
        The get_photos function is used to retrieve all the photos in the database.
        It can be filtered by skip and limit parameters, which are optional.
    
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param current_user: User: Get the current user from the auth_service
    :param db: Session: Get the database session
    :param : Skip the first n photos
    :return: A list of photos
    :doc-author: Trelent
    """
    photos = await repository_photos.get_photos(skip, limit, current_user, db)
    if photos is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found"
        )
    return photos


@router.patch(
    "/add_tags",
    response_model=PhotoResponse,
    status_code=status.HTTP_200_OK,
    summary="Add tags to a photo",
)
async def add_tag(
    body: TagResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The add_tag function adds a tag to the photo.
            The function takes in a TagResponse object, which contains the photo_id and tag name.
            It then checks if the user has access to that particular photo, and if so it will add
            that tag to the database (if it doesn't already exist) and append it to that specific
            photos tags list.
    
    :param body: TagResponse: Get the tag name and photo id from the request body
    :param db: Session: Get access to the database
    :param current_user: User: Get the user that is currently logged in
    :param : Get the tag name and photo id from the request body
    :return: A photo object, which is the same as what the get_photo function returns
    :doc-author: Trelent
    """
    """
    The add_tag function adds a tag to the photo.
        The function takes in a TagResponse object, which contains the photo_id and tag name.
        It then checks if the user has access to that particular photo, and if so it will add
        that tag to the database (if it doesn't already exist) and append it to that specific
        photos tags list.

    :param body: TagResponse: Get the tag name and photo id from the request body
    :param db: Session: Get access to the database
    :param current_user: User: Get the user that is currently logged in
    :return: A photo object
    :doc-author: Trelent
    """

    photo = await repository_photos.get_photo_user(
        photo_id=body.photo_id, db=db, current_user=current_user
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    if len(photo.tags) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 tags are allowed per photo",
        )

    tag = db.query(Tag).filter_by(name=body.tag).first()
    if not tag:
        tag = Tag(name=body.tag)
        db.add(tag)
        db.commit()

    if tag not in photo.tags:
        photo.tags.append(tag)
        photo_data = PhotoUpdate(image_url=photo.image_url, content=photo.content)
        await repository_photos.update_photo(
            photo.id, photo_data=photo_data, current_user=current_user, db=db
        )

    return photo
