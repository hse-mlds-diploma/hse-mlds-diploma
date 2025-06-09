import os
import json
from aiokafka import AIOKafkaConsumer


class ModerationResultsConsumer:
    def __init__(self, review_service, image_service):
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.moderation_results_topic = os.getenv("KAFKA_MODERATION_RESULTS_TOPIC", "moderation-results")
        self.consumer = AIOKafkaConsumer(
            self.moderation_results_topic,
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="product-reviews-moderation-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.review_service = review_service
        self.image_service = image_service

    async def consume(self):
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                moderation_result_data = msg.value
                await self.review_service.handle_moderation_result(moderation_result_data)
                await self.image_service.handle_moderation_result(moderation_result_data)
        finally:
            await self.consumer.stop()
