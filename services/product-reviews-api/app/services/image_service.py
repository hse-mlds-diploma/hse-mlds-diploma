from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.photo import ReviewPhoto
from app.models.enums import PhotoStatus
from app.services.s3_service import S3Service
from app.database import DatabaseManager
from datetime import datetime
import os
from typing import List

class ImageService:
    _instance = None
    _s3_service = None
    _db_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageService, cls).__new__(cls)
            cls._s3_service = S3Service()
            cls._db_manager = DatabaseManager()
        return cls._instance

    def _get_db(self) -> Session:
        return self._db_manager.get_session()

    async def upload_photo(self, file: UploadFile) -> dict:
        db = self._get_db()
        try:
            # Upload file to S3
            file_name = await self._s3_service.upload_file(file)
            if not file_name:
                raise ValueError("Failed to upload file")
            
            # Create photo URL
            photo_url = f"{os.getenv('S3_ENDPOINT')}/{self._s3_service.bucket_name}/{file_name}"
            
            # Create photo record in database
            db_photo = ReviewPhoto(
                photo_url=photo_url,
                status="pending",
                created_at=datetime.now()
            )
            db.add(db_photo)
            db.commit()
            db.refresh(db_photo)
            
            return {
                "photo_id": db_photo.id,
                "photo_url": photo_url
            }
        finally:
            self._db_manager.close_session()

    def get_photo(self, photo_id: int) -> ReviewPhoto:
        db = self._get_db()
        try:
            photo = db.query(ReviewPhoto).filter(ReviewPhoto.id == photo_id).first()
            if photo is None:
                raise ValueError("Photo not found")
            return photo
        finally:
            self._db_manager.close_session()

    def update_photo_status(self, photo_id: int, status: PhotoStatus) -> ReviewPhoto:
        db = self._get_db()
        try:
            photo = self.get_photo(photo_id)
            photo.status = status
            photo.updated_at = datetime.now()
            db.commit()
            db.refresh(photo)
            return photo
        finally:
            self._db_manager.close_session() 
