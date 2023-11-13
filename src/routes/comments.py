from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.comment import CommentRequest, CommentResponse
from src.database import get_db
from src.repositories.comment import CommentRepository

router = APIRouter()
comment_repository = CommentRepository()

@router.post("/comments/", response_model=CommentResponse)
async def create_comment(comment_req: CommentRequest, db: Session = Depends(get_db)):
    # Операція створення коментаря
    comment = comment_repository.create_comment(db, comment_req, user_id=1, photo_id=1)  # Потрібно вказати конкретні user_id та photo_id
    return comment

@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    # Отримання коментаря за його ідентифікатором
    comment = comment_repository.get_comment_by_id(db, comment_id, user_id=1)  # Потрібно вказати конкретний user_id
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_req: CommentRequest, db: Session = Depends(get_db)):
    # Операція оновлення коментаря
    comment = comment_repository.update_comment(db, comment_id, comment_req.content, user_id=1)  # Потрібно вказати конкретний user_id
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.delete("/comments/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    # Операція видалення коментаря
    comment = comment_repository.delete_comment(db, comment_id, user_id=1)  # Потрібно вказати конкретний user_id
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
