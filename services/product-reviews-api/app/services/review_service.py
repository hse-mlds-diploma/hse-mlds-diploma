from datetime import datetime
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.photo import ReviewPhoto
from app.models.enums import ReviewStatus
from app.schemas.review import ReviewCreate
from app.kafka_producer import KafkaProducerService
from app.database import DatabaseManager
from app.services.image_service import ImageService
import os


class ReviewService:
    _instance = None
    _kafka_producer = None
    _db_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReviewService, cls).__new__(cls)
            cls._kafka_producer = KafkaProducerService()
            cls._db_manager = DatabaseManager()
        return cls._instance

    def _get_db(self) -> Session:
        return self._db_manager.get_session()

    def create_review(self, review: ReviewCreate) -> Review:
        db = self._get_db()
        try:
            db_review = Review(
                text=review.text,
                rating=review.rating,
                product_id=review.product_id,
                status="pending",
                created_at=datetime.now()
            )
            db.add(db_review)
            db.commit()
            db.refresh(db_review)

            photo_urls = []
            if review.photo_ids:
                for photo_id in review.photo_ids:
                    photo = db.query(ReviewPhoto).filter(ReviewPhoto.id == photo_id).first()
                    if photo is None:
                        raise ValueError(f"Photo with id {photo_id} not found")
                    photo.review_id = db_review.id
                    photo.updated_at = datetime.now()
                    # Generate public URL for the photo
                    photo_url = photo.photo_url
                    photo_urls.append(photo_url)

            db.commit()
            db.refresh(db_review)

            review_data = {
                'id': db_review.id,
                'text': db_review.text,
                'rating': db_review.rating,
                'product_id': db_review.product_id,
                'status': db_review.status,
                'created_at': db_review.created_at
            }
            print('photo_urls', photo_urls)
            self._kafka_producer.send_review_event(review_data, photo_urls)

            return db_review
        finally:
            self._db_manager.close_session()

    def _patch_photo_urls(self, photos):
        api_base_url = os.getenv('API_BASE_URL', '')
        for photo in photos:
            filename = photo.photo_url.split('/')[-1]
            photo.photo_url = f"{api_base_url}/api/v1/images/file/{filename}"
        return photos

    def get_reviews(self, skip: int = 0, limit: int = 100):
        db = self._get_db()
        try:
            reviews = db.query(Review).offset(skip).limit(limit).all()
            image_service = ImageService()
            result = []
            for review in reviews:
                photos = image_service.get_photos_by_review_id(review.id)
                self._patch_photo_urls(photos)
                review.photos = photos
                result.append(review)
            return result
        finally:
            self._db_manager.close_session()

    def get_review(self, review_id: int):
        db = self._get_db()
        try:
            review = db.query(Review).filter(Review.id == review_id).first()
            if review is None:
                raise ValueError("Review not found")
            image_service = ImageService()
            photos = image_service.get_photos_by_review_id(review.id)
            self._patch_photo_urls(photos)
            review.photos = photos
            return review
        finally:
            self._db_manager.close_session()

    def update_review_status(self, review_id: int, status: ReviewStatus) -> Review:
        db = self._get_db()
        try:
            review = self.get_review(review_id)
            review.status = status
            review.updated_at = datetime.now()
            db.commit()
            db.refresh(review)
            return review
        finally:
            self._db_manager.close_session()

    def __del__(self):
        if self._kafka_producer:
            self._kafka_producer.close()
