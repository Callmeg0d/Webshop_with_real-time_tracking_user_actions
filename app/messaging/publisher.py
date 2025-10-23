from pydantic import EmailStr

from app.messaging.broker import broker


async def publish_registration_confirmation(email: EmailStr):
    await broker.publish(
        message=email,
        topic="registration_confirmation"
    )

async def publish_order_confirmation(order: dict, email: EmailStr):
    await broker.publish(
        message={"order": order, "email_to": email},
        topic="order_confirmation"
    )