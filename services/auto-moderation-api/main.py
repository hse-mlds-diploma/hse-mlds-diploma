from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
from app.consumers.review_consumer import ReviewConsumer
from app.services.moderation_service import ModerationService

load_dotenv()

app = FastAPI(
    title="Auto Moderation API",
    description="API for automatic moderation of product reviews",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

moderation_service = ModerationService()
review_consumer = ReviewConsumer(moderation_service)


@app.on_event("startup")
async def startup_event():
    # Start Kafka consumer in the background
    asyncio.create_task(review_consumer.consume())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
