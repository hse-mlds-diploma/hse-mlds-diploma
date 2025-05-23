from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import PhotoStatus


class ReviewPhoto(Base):
    __tablename__ = "review_photos"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=False)
    status = Column(String, nullable=False, default=PhotoStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
