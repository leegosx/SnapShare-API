from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import tags as repository_tags
from src.schemas.tag import TagRequest, TagResponse, TagModel

router = APIRouter(prefix='/tags', tags=["tags"])


@router.get("/", response_model=List[TagModel])
async def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    The read_tags function returns a list of tags.
        ---
        get:
          summary: Returns a list of tags.
          description: Get all the available tags in the database, with pagination support.
          responses:
            &quot;200&quot;:
              description: A JSON array containing tag objects (see below).  Each object has an id and name field, as well as an optional color field if one was specified when creating the tag.  The response also includes a total_count field indicating how many total results there are for this query (which may be more than what is returned in this response).
    
    :param skip: int: Skip a number of tags
    :param limit: int: Limit the number of tags returned
    :param db: Session: Get the database session
    :return: A list of tag objects
    """
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagModel)
async def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The read_tag function returns a single tag from the database.
        The function takes in an integer, which is the id of the tag to be returned.
        If no such tag exists, then a 404 error is raised.
    
    :param tag_id: int: Specify the id of the tag to be read
    :param db: Session: Pass the database session to the repository layer
    :return: A tag object
    """
    
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagModel)
async def create_tag(body: TagRequest, db: Session = Depends(get_db)):
    """
    The create_tag function creates a new tag in the database.
        The function takes a TagRequest object as input and returns the newly created tag.
    
    :param body: TagRequest: Get the data from the request body
    :param db: Session: Get the database session
    :return: A tag object
    """
    tag = await repository_tags.create_tag(body, db)
    return tag


@router.put("/{tag_id}", response_model=TagModel)
async def update_tag(body: TagRequest, tag_id: int, db: Session = Depends(get_db)):
    """
    The update_tag function updates a tag in the database.
        The function takes a TagRequest object as input, which contains the new values for the tag.
        It also takes an integer representing the id of the tag to be updated.
        If no such id exists, it raises an HTTPException with status code 404 and detail &quot;Tag not found&quot;.
    
    
    :param body: TagRequest: Get the body of the request
    :param tag_id: int: Specify the tag id of the tag to be updated
    :param db: Session: Pass the database session to the repository
    :return: A tag object, which is a pydantic model
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", response_model=TagModel)
async def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The remove_tag function removes a tag from the database.
        Args:
            tag_id (int): The id of the tag to be removed.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    :param tag_id: int: Specify the id of the tag to be removed
    :param db: Session: Pass the database connection to the repository
    :return: A tag object
    :doc-author: Trelent
    """

    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag