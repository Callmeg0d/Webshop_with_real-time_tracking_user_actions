from pydantic import EmailStr

from app.messaging.broker import broker


async def publish_registration_confirmation(email: EmailStr) -> None:
    await broker.publish(
        message=email,
        topic="registration_confirmation",
    )

