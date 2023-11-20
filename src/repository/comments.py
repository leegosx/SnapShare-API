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
    return db.query(Comment).filter(Comment.id==comment_id).first()

async def get_comments(
    image_id: int, 
    db: Session
    ) -> List[Comment]:
    return db.query(Comment).filter(Comment.image_id==image_id).limit(None).all()

async def create_comment(
                         body: CommentRequest, 
                         user: User, 
                         image_id: int, 
                         db: Session
                         ) -> Comment:
    comment = Comment(content=body.content, user_id=user.id, image_id=image_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

async def update_comment(
    body: CommentRequest, 
    comment_id: int, db: Session
    ):
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        comment.content = body.content
        db.commit()
    return comment

async def delete_comment(
    comment_id: int, 
    db: Session
    ) :
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
