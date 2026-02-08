from faststream.kafka import KafkaRouter
from shared import ReserveStockResult, get_logger

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_stock_reserved, publish_stock_reservation_failed

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


@router.subscriber("order_processing_started", group_id="product_service")
async def handle_order_processing_started(event: dict) -> None:
    """Обработчик события начала обработки заказа — резервирует товары."""
    order_id = event.get("order_id")
    order_items = event.get("order_items", [])

    if not order_id or not order_items:
        logger.warning(
            "Received order_processing_started event without order_id or order_items",
            extra={"event": event},
        )
        return

    logger.info(f"Processing stock reservation for order {order_id}, items: {len(order_items)}")

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                service = container.stock_reservation_service()
                result, error_msg = await service.reserve_stock(order_id, order_items)
            await session.commit()

            if result in (ReserveStockResult.ALREADY_DONE, ReserveStockResult.SUCCESS):
                await publish_stock_reserved(order_id)
                if result == ReserveStockResult.ALREADY_DONE:
                    logger.debug(f"Order {order_id} already processed, confirming reservation")
                else:
                    logger.info(f"Stock reservation completed successfully for order {order_id}")
            else:
                logger.warning(f"Stock reservation failed for order {order_id}: {error_msg}")
                await publish_stock_reservation_failed(order_id, error_msg or "Insufficient stock")
    except Exception as e:
        logger.error(f"Error processing stock reservation for order {order_id}: {e}", exc_info=True)
        await publish_stock_reservation_failed(order_id, str(e))


@router.subscriber("stock_increase", group_id="product_service")
async def handle_stock_increase(request: dict) -> None:
    """Обработчик события возврата товаров (компенсация)."""
    order_id = request.get("order_id")
    product_id = request.get("product_id")
    quantity = request.get("quantity")

    if not order_id or not product_id or not quantity:
        logger.warning(
            "Received stock_increase event without required fields",
            extra={"request": request},
        )
        return

    logger.info(
        f"Processing stock increase (compensation) for order {order_id}, "
        f"product {product_id}, quantity {quantity}"
    )

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                service = container.stock_reservation_service()
                recorded = await service.record_stock_compensation(order_id, product_id, quantity)
            await session.commit()
            if recorded:
                logger.info(
                    f"Stock increase (compensation) completed for order {order_id}, product {product_id}"
                )
            else:
                logger.debug(f"Compensation already processed for order {order_id}, product {product_id}")
    except Exception as e:
        logger.error(
            f"Error processing stock increase for order {order_id}, product {product_id}: {e}",
            exc_info=True,
        )
        raise
