from app.messaging.broker import broker


async def publish_stock_reserved(order_id: int) -> None:
    """Публикует событие успешной резервации товаров."""
    await broker.publish(
        message={"order_id": order_id},
        topic="stock_reserved",
    )


async def publish_stock_reservation_failed(order_id: int, reason: str) -> None:
    """Публикует событие неудачной резервации товаров."""
    await broker.publish(
        message={"order_id": order_id, "reason": reason},
        topic="stock_reservation_failed",
    )

