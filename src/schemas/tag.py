from pydantic import BaseModel

class Tag(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: int
    tag: str
    photo_id: int
    
    class Config:
        from_attributes = True