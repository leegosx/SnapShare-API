from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from src.models.base import Base
from typing import Optional, List
from datetime import datetime

from src.database.db import get_db
from src.models.user import User
from src.repository.search_filter import get_images_by_search

router = APIRouter(prefix="/search_filter", tags=["search_filter"])

@router.get("/search/")
async def search_images(
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    min_rating: int = Query(0, description="Minimum rating"),
    max_rating: int = Query(5, description="Maximum rating"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Perform the search based on the query and filter parameters
    if tag is None and keyword is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one of tag or keyword must be provided")

    images = get_images_by_search(db, tag, keyword, min_rating, max_rating, start_date, end_date)
    
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No images with rating found")
    
    return images
