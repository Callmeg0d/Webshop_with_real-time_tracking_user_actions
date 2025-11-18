from typing import Any, Dict

from pydantic import EmailStr

from app.messaging.broker import broker


async def publish_registration_confirmation(email: EmailStr) -> None:
    await broker.publish(
        message=email,
        topic="registration_confirmation",
    )


async def publish_order_confirmation(order: dict, email: EmailStr) -> None:
    await broker.publish(
        message={"order": order, "email_to": email},
        topic="order_confirmation",
    )

async def publish_tracker_event(event: Dict[str, Any], topic: str) -> None:
    """Публикация любого события трекера в указанный Kafka-топик."""
    await broker.publish(
        message=event,
        topic=topic,
    )