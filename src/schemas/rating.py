from typing import List
from pydantic import BaseModel, Field

class RatingRequest(BaseModel):
    # rating: int = Field(ge=1, le=5)
    rating: int
    
class RatingResponse(BaseModel):
    id: int
    user_id: int
    image_id: int
    rating_score: int
    
class ImageRatingsResponse(BaseModel):
    id: int
    user_id: int
    image_id: int
    rating_score: int
    average_rating: float
    
class AllRatingResponse(BaseModel):
    id: int
    user_id: int
    image_id: int
    rating_score: int
    