from pydantic import EmailStr

from app.messaging.broker import broker


async def publish_order_confirmation(order: dict, email: EmailStr) -> None:
    await broker.publish(
        message={"order": order, "email_to": email},
        topic="order_confirmation",
    )

