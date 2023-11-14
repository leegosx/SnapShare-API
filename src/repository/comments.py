from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.comment import Comment
from src.schemas.comment import CommentRequest

async def create_comment(db: Session, comment: CommentRequest, user_id: int, photo_id: int) -> Comment:
    db_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    print('Create')
    return db_comment

async def get_comment_by_id(db: Session, comment_id: int, user_id: int) -> Comment:
    if comment_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment id is required')
    print('get')
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user_id)).first()

async def update_comment(db: Session, comment_id: int, new_content: str, user_id: int) -> Comment:
    comment = await get_comment_by_id(db, comment_id, user_id)
    print('update')
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    if comment:
        comment.content = new_content
        await db.commit()
        await db.refresh(comment)
    return comment

async def delete_comment(db: Session, comment_id: int, user_id: int) -> Comment:
    comment = await get_comment_by_id(db, comment_id, user_id)
    print('delete')
    if comment_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment id is required')
    if comment:
        db.delete(comment)
        await db.commit()
    return comment
