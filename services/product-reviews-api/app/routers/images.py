from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models.enums import PhotoStatus
from app.schemas.photo import PhotoResponse
from app.services.image_service import ImageService
from pydantic import BaseModel
from app.services.s3_service import S3Service
from fastapi.responses import StreamingResponse

router = APIRouter()


class PhotoUploadResponse(BaseModel):
    photo_id: int
    photo_url: str


def get_image_service():
    return ImageService()


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    image_service: ImageService = Depends(get_image_service)
):
    try:
        return await image_service.upload_photo(file)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: int,
    image_service: ImageService = Depends(get_image_service)
):
    try:
        return image_service.get_photo(photo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{photo_id}/status", response_model=PhotoResponse)
async def update_photo_status(
    photo_id: int,
    status: PhotoStatus,
    image_service: ImageService = Depends(get_image_service)
):
    try:
        return image_service.update_photo_status(photo_id, status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/bucket-files")
def list_bucket_files():
    s3_service = S3Service()
    files = s3_service.list_bucket_files()
    return {"files": files}


@router.get("/file/{filename}")
def get_image_file(filename: str):
    s3_service = S3Service()
    file_stream, content_type = s3_service.get_file_stream(filename)
    if file_stream is None:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(file_stream, media_type=content_type)
