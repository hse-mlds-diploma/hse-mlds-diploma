from kafka import KafkaProducer
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
import os

load_dotenv()


class KafkaProducerService:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_REVIEWS_TOPIC', 'product-reviews')
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_review_event(self, review_data: Dict[str, Any], photo_urls: List[str] = None) -> None:
        """
        Send review event to Kafka topic
        """
        event = {
            'id': review_data['id'],
            'text': review_data['text'],
            'rating': review_data['rating'],
            'product_id': review_data['product_id'],
            'status': review_data['status'],
            'created_at': review_data['created_at'].isoformat(),
            'photo_urls': photo_urls or [],
            'event_type': 'REVIEW_CREATED'
        }

        self.producer.send(self.topic, value=event)
        self.producer.flush()

    def close(self) -> None:
        """
        Close Kafka producer connection
        """
        self.producer.close()
