from app.messaging.broker import broker


async def publish_tracker_event(event: dict, topic: str) -> None:
    """Публикация события трекера в указанный Kafka-топик."""
    await broker.publish(
        message=event,
        topic=topic,
    )

