from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReviewBase(BaseModel):
    product_id: int
    rating: int
    text: str

class ReviewCreate(ReviewBase):
    photo_ids: Optional[List[int]] = None

class ReviewResponse(ReviewBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 