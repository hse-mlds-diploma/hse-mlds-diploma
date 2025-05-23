from aiokafka import AIOKafkaConsumer
from aiokafka import AIOKafkaProducer
import json
import os


class ReviewConsumer:
    def __init__(self, moderation_service):
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.reviews_topic = os.getenv("KAFKA_REVIEWS_TOPIC", "product-reviews-api")
        self.moderation_results_topic = os.getenv("KAFKA_MODERATION_RESULTS_TOPIC", "moderation-results")
        self.consumer = AIOKafkaConsumer(
            self.reviews_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="auto-moderation-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.moderation_service = moderation_service

    async def consume(self):
        await self.consumer.start()
        await self.producer.start()
        try:
            async for msg in self.consumer:
                review_data = msg.value

                moderation_result = await self.moderation_service.moderate_review(
                    review_data.get("text"),
                    review_data.get("photo_urls", [])
                )

                await self.producer.send_and_wait(
                    self.moderation_results_topic,
                    {
                        "review_id": review_data.get("id"),
                        "moderation_result": moderation_result
                    }
                )
        finally:
            await self.consumer.stop()
            await self.producer.stop()
