from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import images, reviews
from app.services.review_service import ReviewService
from app.services.image_service import ImageService
from app.consumers.moderation_results_consumer import ModerationResultsConsumer
import asyncio

load_dotenv()

app = FastAPI(
    title="Product Reviews API",
    description="API for managing product reviews",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(images.router, prefix="/api/v1/images", tags=["images"])


@app.on_event("startup")
async def startup_event():
    review_service = ReviewService()
    image_service = ImageService()
    moderation_consumer = ModerationResultsConsumer(review_service, image_service)
    asyncio.create_task(moderation_consumer.consume())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
