from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.comment import CommentRequest, CommentResponse
from src.database.db import get_db
from src.repository.comments import (
    create_comment,
    get_comment,
    List,
    get_comments,
    update_comment,
    delete_comment
)

from src.services.auth_service import auth_service
from src.models.user import User, UserRole


router = APIRouter(prefix='/comments', tags=["comments"])

@router.get("/all", response_model = List[CommentResponse])
async def read_comments(
    image_id: int = 0, 
    db: Session = Depends(get_db)
    ):
    if not image_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='image id is required')
    image = repository_images.get_image(image_id, db)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    comments = repository_comments.get_comments(image_id, db)
    return comments

@router.post("/", response_model=CommentResponse)
async def create_comment(
    body: CommentRequest, 
    image_id: int = 0, 
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
    ):
    if image_id == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='image id is required')
    image = repository_images.get_image(image_id=image_id, db=db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return repository_comments.create_comment(body, current_user, image_id, db)

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(body: CommentRequest, 
                         comment_id: int, 
                         db: Session = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    comment = repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this comment")
    new_comment = repository_comments.update_comment(body, comment_id, db)
    return new_comment

@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db)
    ):
    comment = repository_comments.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

# @router.delete("/{comment_id}", response_model=CommentResponse, dependencies=[Depends(roles.Roles(['admin', 'moderator']))])
# async def delete_comment(
#     comment_id: int, 
#     db: Session = Depends(get_db)
#     ):
#     comment = repository_comments.delete_comment(comment_id, db)
#     if not comment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
#     return comment
