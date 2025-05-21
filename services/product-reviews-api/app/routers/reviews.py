from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.enums import ReviewStatus
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()

def get_review_service():
    return ReviewService()

@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        return review_service.create_review(review)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    review_service: ReviewService = Depends(get_review_service)
):
    return review_service.get_reviews(skip, limit)

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        return review_service.get_review(review_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{review_id}/status", response_model=ReviewResponse)
async def update_review_status(
    review_id: int,
    status: ReviewStatus,
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        return review_service.update_review_status(review_id, status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
