from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import ReviewStatus


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default=ReviewStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Временное поле для сериализации
    photos = None
