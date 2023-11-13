from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.comment import Comment
from src.schemas.comment import CommentRequest

class CommentRepository:
    def create_comment(self, db: Session, comment: CommentRequest, user_id: int, photo_id: int) -> Comment:
        db_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def get_comment_by_id(self, db: Session, comment_id: int, user_id: int) -> Comment:
        return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user_id)).first()

    def update_comment(self, db: Session, comment_id: int, new_content: str, user_id: int) -> Comment:
        comment = self.get_comment_by_id(db, comment_id, user_id)
        if comment:
            comment.content = new_content
            db.commit()
            db.refresh(comment)
        return comment

    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> Comment:
        comment = self.get_comment_by_id(db, comment_id, user_id)
        if comment:
            db.delete(comment)
            db.commit()
        return comment

    def get_comments_for_photo(self, db: Session, photo_id: int) -> List[Comment]:
        return db.query(Comment).filter(Comment.photo_id == photo_id).all()
