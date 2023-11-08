from pydantic import BaseModel

class Tag(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: int
    tags: str
    
    class Config:
        from_attributes = True