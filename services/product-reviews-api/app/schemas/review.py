from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.photo import PhotoResponse


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
    photos: Optional[List[PhotoResponse]] = None

    class Config:
        from_attributes = True
