from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.comment import CommentRequest, CommentResponse
from src.database.db import get_db

from src.repository import comments as repository_comments
from src.repository import images as repository_images

from src.services.auth_service import auth_service
from src.models.user import User, UserRole
from src.services import roles

router = APIRouter(prefix='/comments', tags=["comments"])

@router.get("/all/", response_model = List[CommentResponse])
async def read_comments(
    image_id: int = 0, 
    db: Session = Depends(get_db)
    ):
    """
    The read_comments function returns a list of comments for the image with the given ID.
    
    :param image_id: int: Specify the image id for which we want to get comments
    :param db: Session: Pass the database session to the function
    :return: A list of comments
    """
    if not image_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Image ID is required')
    image = await repository_images.get_image(image_id, db)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    comments = await repository_comments.get_comments(image_id, db)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments have been found for this photo")
    return comments

@router.get("/get/{comment_id}/", response_model=CommentResponse)
async def read_comment(
    comment_id: int = 0,
    db: Session = Depends(get_db)
    ):
    """
    The read_comment function returns a single comment from the database.
    
    :param comment_id: int: Pass the comment id to the function
    :param db: Session: Pass the database session to the function
    :return: A comment object
    """
    if not comment_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment ID is required')
    comment = await repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment
    
@router.post("/add_comments/", response_model=CommentResponse)
async def create_comment(
    body: CommentRequest, 
    image_id: int = 0, 
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    The create_comment function creates a new comment for an image.
    The function takes in the following parameters:
    body: CommentRequest - A request object containing the comment's text and user_id.
    image_id: int - An integer representing the id of an existing image to which we want to add a comment. 
    This parameter is optional, but if it is not provided, then we will raise a 400 error (bad request).
    current_user: User = Depends(auth_service.get_current_user) - A user object that represents our currently logged-in user (if any
    
    :param body: CommentRequest: Validate the request body
    :param image_id: int: Get the image id from the url
    :param current_user: User: Get the user who is making the request
    :param db: Session: Pass the database session to the repository layer
    :return: A comment object
    """

    if image_id == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Image id is required')
    image = await repository_images.get_image(image_id=image_id, db=db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return await repository_comments.create_comment(body, current_user, image_id, db)

@router.put("/update/{comment_id}/", response_model=CommentResponse)
async def update_comment(body: CommentRequest, 
                         comment_id: int, 
                         db: Session = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The update_comment function updates a comment in the database.
    The function takes in a CommentRequest object, which contains the new text for the comment.
    It also takes in an integer representing the id of the comment to be updated. 
    The function returns an updated Comment object.
    
    :param body: CommentRequest: Get the data from the request body
    :param comment_id: int: Identify which comment is being updated
    :param db: Session: Pass the database session into the function
    :param current_user: User: Check if the user is logged in and has permission to delete a comment
    :return: A comment object, which is passed to the response
    """
    comment = await repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this comment")
    new_comment = await repository_comments.update_comment(body, comment_id, db)
    return new_comment

@router.delete("/remove/{comment_id}/", response_model=CommentResponse,
               dependencies=[Depends(roles.Roles(["admin", "moderator"]))])
async def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db)
    ):
    """
    The delete_comment function deletes a comment from the database.
    Args:
    comment_id (int): The id of the comment to be deleted.
    db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
    Returns:
    Comment: The deleted Comment object.
    
    :param comment_id: int: Pass in the id of the comment to be deleted
    :param db: Session: Pass the database session to the repository function
    :return: A comment object
    :doc-author: Trelent
    """
    
    comment = await repository_comments.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment