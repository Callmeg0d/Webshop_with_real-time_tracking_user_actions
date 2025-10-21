from app.messaging.broker import broker


async def publish_registration_confirmation():
    await broker.publish(
        message="kaka",
        topic="registation_confirmation"
    )

async def publish_order_confirmation():
    await broker.publish(
        message="gaga",
        topic="order_confirmation"
    )