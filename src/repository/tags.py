from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.image import Tag
from src.schemas.tag import TagRequest

async def get_tags(offset: int, limit: int, db: Session):
    """
    The get_tags function returns a list of tags from the database.
        
    
    :param offset: int: Specify the starting point of the query
    :param limit: int: Limit the number of tags returned
    :param db: Session: Pass the database session to the function
    :return: A list of strings, so the return type is list[str]
    """
    sq = select(Tag).offset(offset).limit(limit)
    tags = db.execute(sq)
    return tags.scalars().all()

async def get_tag(tag_id: int, db: Session):
    """
    The get_tag function returns a single tag from the database.
        
    
    :param tag_id: int: Specify the id of the tag we want to get
    :param db: Session: Pass the database session to the function
    :return: A sqlalchemy object
    """
    sq = select(Tag).filter_by(id=tag_id)
    tag = db.execute(sq)
    return tag.scalar_one_or_none()

async def create_tag(body: TagRequest, db: Session):
    """
    The create_tag function creates a new tag in the database.
    
    :param body: TagRequest: Get the name of the tag from the request body
    :param db: Session: Pass the database session to the function
    :return: A tag, so the return type of create_tag_handler should be tag
    """
    tag = db.query(Tag).filter_by(name=body.name).first()
    if tag is None:
        tag = Tag(name=body.name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag

async def update_tag(tag_id: int, body: TagRequest, db: Session):
    """
    The update_tag function updates a tag in the database.
        
    
    :param tag_id: int: Identify the tag to be updated
    :param body: TagRequest: Pass the data to be updated
    :param db: Session: Access the database
    :return: The updated tag
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag .name = body.name
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session):
    """
    The remove_tag function removes a tag from the database.
        
    
    :param tag_id: int: Specify the id of the tag to be deleted
    :param db: Session: Pass a database session to the function
    :return: The tag that was removed
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag