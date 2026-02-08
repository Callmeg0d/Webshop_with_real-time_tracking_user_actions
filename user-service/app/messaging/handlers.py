from faststream.kafka import KafkaRouter
from shared import ReserveBalanceResult, get_logger

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_balance_reserved, publish_balance_reservation_failed

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


@router.subscriber("order_processing_started", group_id="user_service")
async def handle_order_processing_started(event: dict) -> None:
    """Обработчик события начала обработки заказа — резервирует баланс."""
    order_id = event.get("order_id")
    user_id = event.get("user_id")
    total_cost = event.get("total_cost")

    if not order_id or not user_id or not total_cost:
        logger.warning("Received order_processing_started event without required fields", extra={"event": event})
        return

    logger.info(f"Processing balance reservation for order {order_id}, user {user_id}, cost: {total_cost}")

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                service = container.balance_reservation_service()
                result = await service.reserve_balance(order_id, user_id, total_cost)
            await session.commit()

            if result in (ReserveBalanceResult.ALREADY_DONE, ReserveBalanceResult.SUCCESS):
                await publish_balance_reserved(order_id)
                if result == ReserveBalanceResult.ALREADY_DONE:
                    logger.debug(f"Order {order_id} already processed, confirming reservation")
                else:
                    logger.info(f"Balance reservation completed successfully for order {order_id}")
            else:
                reason = (
                    f"User {user_id} not found" if result == ReserveBalanceResult.USER_NOT_FOUND
                    else "Insufficient balance"
                )
                logger.warning(f"Balance reservation failed for order {order_id}: {reason}")
                await publish_balance_reservation_failed(order_id, reason)
    except Exception as e:
        logger.error(f"Error processing balance reservation for order {order_id}: {e}", exc_info=True)
        await publish_balance_reservation_failed(order_id, str(e))


@router.subscriber("balance_increase", group_id="user_service")
async def handle_balance_increase(request: dict) -> None:
    """Обработчик события возврата баланса (компенсация)."""
    order_id = request.get("order_id")
    user_id = request.get("user_id")
    amount = request.get("amount")

    if not order_id or not user_id or not amount:
        logger.warning("Received balance_increase event without required fields", extra={"request": request})
        return

    logger.info(f"Processing balance increase (compensation) for order {order_id}, user {user_id}, amount: {amount}")

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                service = container.balance_reservation_service()
                recorded = await service.record_balance_compensation(order_id, user_id, amount)
            await session.commit()
            if recorded:
                logger.info(f"Balance increase (compensation) completed for order {order_id}, user {user_id}")
            else:
                logger.debug(f"Compensation already processed for order {order_id}")
    except Exception as e:
        logger.error(f"Error processing balance increase for order {order_id}, user {user_id}: {e}", exc_info=True)
        raise
