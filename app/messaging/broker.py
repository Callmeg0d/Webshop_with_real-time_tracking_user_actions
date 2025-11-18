from faststream.kafka import KafkaBroker

from app.config import settings

broker = KafkaBroker(f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
