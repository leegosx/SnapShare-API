from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.comment import CommentRequest, CommentResponse
from src.database.db import get_db
from src.repository.comments import (
    create_comment,
    get_comment_by_id,
    update_comment,
    delete_comment
)

router = APIRouter()

@router.post("/comments/", response_model=CommentResponse)
async def create_comment(comment_req: CommentRequest, db: Session = Depends(get_db)):
    # Операція створення коментаря
    # user_id та photo_id можна отримати з контексту аутентифікації, якщо потрібно
    user_id = 1  # Приклад фіксованого значення user_id
    photo_id = 1  # Приклад фіксованого значення photo_id
    comment = await create_comment(db, comment_req, user_id=user_id, photo_id=photo_id)
    return comment

@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    # Отримання коментаря за його ідентифікатором
    if comment_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment id is required')
    user_id = 1  # Приклад фіксованого значення user_id
    comment = await get_comment_by_id(db, comment_id, user_id=user_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_req: CommentRequest, db: Session = Depends(get_db)):
    # Операція оновлення коментаря
    if comment_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment id is required')
    user_id = 1  # Приклад фіксованого значення user_id
    comment = await update_comment(db, comment_id, comment_req.content, user_id=user_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.delete("/comments/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    # Операція видалення коментаря
    if comment_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment id is required')
    user_id = 1  # Приклад фіксованого значення user_id
    comment = await delete_comment(db, comment_id, user_id=user_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
