from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.models.user import User
from src.models.photo import Photo, Tag
from src.schemas.photo import PhotoBase, PhotoCreate, PhotoResponse, PhotoUpdate
from src.schemas.tag import TagResponse
from src.repository import photos as repository_photos
from src.services.auth_service import Auth

router = APIRouter(prefix="/photos", tags=["photos"])


# Add the Auth service as a dependency
def get_current_user(auth: Auth = Depends(Auth.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        function below. It will return the current user object, or None if no user
        is logged in.

    :param auth: Auth: Get the current user
    :return: An auth object
    :doc-author: Trelent
    """
    return auth


@router.post("/create_new", response_model=PhotoResponse)
async def create_photo(
    body: PhotoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The create_photo function creates a new photo in the database.
        The function takes in a PhotoCreate object, which is validated by pydantic.
        The current_user and db are passed into the create_contact function from repository_photos.

    :param body: PhotoCreate: Get the data from the request body
    :param current_user: User: Get the current user
    :param db: Session: Pass the database session to the repository layer
    :param : Get the current user from the database
    :return: A photo object
    :doc-author: Trelent
    """
    return await repository_photos.create_photo(body, current_user, db)


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    image_url: str,
    body: PhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_photo function updates a photo in the database.
        Args:
            image_url (str): The URL of the photo to be updated.
            body (PhotoUpdate): The new information for the photo.
            current_user (User = Depends(get_current_user)): The user making this request, as determined by get_current_user().
            db (Session = Depends(get-db)): A database session object, as determined by get-db().

    :param image_url: str: Find the photo in the database
    :param body: PhotoUpdate: Pass the data from the request body to update_photo function
    :param current_user: User: Get the current user
    :param db: Session: Pass the database session to the repository layer
    :param : Get the current user from the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_photos.update_photo(image_url, body, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return contact


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def delete_photo(
    image_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The delete_photo function deletes a photo from the database.
        Args:
            image_url (str): The URL of the photo to be deleted.
            current_user (User): The user who is deleting the photo.
            db (Session): A database session object for interacting with the database.

    :param image_url: str: Get the image url from the request body
    :param current_user: User: Get the user id of the current user
    :param db: Session: Get the database session
    :param : Get the current user and the parameter is used to get a database session
    :return: A contact object
    :doc-author: Trelent
    """
    photo = await repository_photos.delete_photo(image_url, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(image_url: str, db: Session = Depends(get_db)):
    """
    The get_photo function returns a photo object from the database.
        The function takes an image_url as input and uses it to query the database for a matching photo.
        If no match is found, then an HTTPException is raised with status code 404 and detail &quot;Photo not found&quot;.


    :param image_url: str: Specify the image url of the photo to be retrieved
    :param db: Session: Pass the database session to the repository layer
    :return: A photo object
    :doc-author: Trelent
    """
    photo = await repository_photos.get_photo(image_url, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/photos", response_model=PhotoResponse)
async def get_photos(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    The get_photos function returns a list of photos for the current user.
        The function is called by the get_photos endpoint, which is defined in main.py.

    :param current_user: User: Get the current user
    :param db: Session: Get the database session
    :return: A list of photos
    :doc-author: Trelent
    """
    photos = await repository_photos.get_photos(current_user, db)
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
    current_user: User = Depends(get_current_user),
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
    :return: A photo object
    :doc-author: Trelent
    """

    photo = await repository_photos.get_photo_user(
        photo_id=body.photo_id, current_user=current_user, db=db
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
        photo_data = PhotoUpdate(content=photo.content)
        await repository_photos.update_photo(
            photo_id=photo.id, photo_data=photo_data, current_user=current_user, db=db
        )

    return photo
