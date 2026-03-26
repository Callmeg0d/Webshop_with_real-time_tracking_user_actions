from faststream.kafka import KafkaBroker

from config import settings

broker: KafkaBroker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
