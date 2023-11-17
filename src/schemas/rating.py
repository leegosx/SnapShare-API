from pydantic import BaseModel, Field

class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    
class RatingResponse(BaseModel):
    id: int
    user_id: int
    image_id: int