from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.comment import Comment
from src.models.user import User
from src.schemas.comment import CommentRequest


async def get_comment(
    comment_id: int, 
    db: Session
    ):
    """
    The get_comment function returns a comment object from the database.
        Args:
            comment_id (int): The id of the comment to be returned.
            db (Session): A connection to the database.
        Returns:
            Comment: The requested Comment object.
    
    :param comment_id: int: Specify the id of the comment to be retrieved from the database
    :param db: Session: Pass the database session to the function
    :return: A comment object
    """
    return db.query(Comment).filter(Comment.id==comment_id).first()

async def get_comments(
    image_id: int, 
    db: Session
    ) -> List[Comment]:
    """
    The get_comments function returns a list of comments for the image with the given id.
        Args:
            image_id (int): The id of an image in the database.
            db (Session): A database session object to query from.
        Returns:
            List[Comment]: A list of Comment objects that are associated with the given image_id.
    
    :param image_id: int: Filter the comments by image_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments
    """
    return db.query(Comment).filter(Comment.image_id==image_id).limit(None).all()

async def create_comment(
                         body: CommentRequest, 
                         user: User, 
                         image_id: int, 
                         db: Session
                         ) -> Comment:
    """
    The create_comment function creates a new comment in the database.
        Args:
            body (CommentRequest): The request body containing the content of the comment.
            user (User): The user who is creating this comment.
            image_id (int): The id of the image that this comment belongs to.
            db (Session): A database session object for interacting with our SQLite3 database file, images_api/db/images-database.sqlite3 . 
    
    :param body: CommentRequest: Get the content of the comment
    :param user: User: Get the user_id of the user who is making a comment
    :param image_id: int: Get the image id from the database
    :param db: Session: Pass the database session to the function
    :return: A comment object
    """
    comment = Comment(content=body.content, user_id=user.id, image_id=image_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

async def update_comment(
    body: CommentRequest, 
    comment_id: int, db: Session
    ):
    """
    The update_comment function updates a comment in the database.
        Args:
            body (CommentRequest): The updated comment object.
            comment_id (int): The id of the comment to update. 
            db (Session): A connection to the database session.
    
    :param body: CommentRequest: Get the content of the comment from the request body
    :param comment_id: int: Find the comment in the database
    :param db: Session: Access the database
    :return: A comment object
    """
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        comment.content = body.content
        db.commit()
    return comment

async def delete_comment(
    comment_id: int, 
    db: Session
    ) :
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_id (int): The id of the comment to be deleted.
            db (Session): A connection to the database.
        Returns: 
            Comment: The deleted Comment object.
    
    :param comment_id: int: Find the comment in the database
    :param db: Session: Pass the database session to the function
    :return: The comment that was deleted
    """
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
