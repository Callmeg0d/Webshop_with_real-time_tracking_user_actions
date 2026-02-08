from faststream.kafka import KafkaRouter
from shared import get_logger

from app.constants import OrderStatus
from app.database import async_session_maker
from app.core.container import Container

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


@router.subscriber("stock_reserved", group_id="order_service")
async def handle_stock_reserved(event: dict) -> None:
    """
    Обработчик события успешной резервации товаров.
    """
    order_id = event.get("order_id")
    if not order_id:
        logger.warning("Received stock_reserved event without order_id", extra={"event": event})
        return

    logger.info(f"Processing stock reservation for order {order_id}")

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                order_service = container.order_service()
                saga_repo = container.saga_reservation_repository()
                order = await order_service.orders_repository.get_order_by_id(order_id)
                if not order or order.status != OrderStatus.PENDING:
                    logger.debug(
                        f"Order {order_id} already processed (status: {order.status if order else 'not found'})"
                    )
                    return
                await saga_repo.set_stock_done(order_id)
                await session.commit()

        logger.info(f"Stock reservation confirmed for order {order_id}")
        await _check_and_confirm_order(order_id)

    except Exception as e:
        logger.error(f"Error processing stock reservation for order {order_id}: {e}", exc_info=True)
        raise


@router.subscriber("balance_reserved", group_id="order_service")
async def handle_balance_reserved(event: dict) -> None:
    """
    Обработчик события успешной резервации баланса.
    """
    order_id = event.get("order_id")
    if not order_id:
        logger.warning("Received balance_reserved event without order_id", extra={"event": event})
        return

    logger.info(f"Processing balance reservation for order {order_id}")

    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                order_service = container.order_service()
                saga_repo = container.saga_reservation_repository()
                order = await order_service.orders_repository.get_order_by_id(order_id)
                if not order or order.status != OrderStatus.PENDING:
                    logger.debug(
                        f"Order {order_id} already processed (status: {order.status if order else 'not found'})"
                    )
                    return
                await saga_repo.set_balance_done(order_id)
                await session.commit()

        logger.info(f"Balance reservation confirmed for order {order_id}")
        await _check_and_confirm_order(order_id)

    except Exception as e:
        logger.error(f"Error processing balance reservation for order {order_id}: {e}", exc_info=True)
        raise


@router.subscriber("stock_reservation_failed", group_id="order_service")
async def handle_stock_reservation_failed(event: dict) -> None:
    """
    Обработчик события неудачной резервации товаров - отменяет заказ.
    
    Args:
        event: Словарь с полями order_id, reason
    """
    order_id = event.get("order_id")
    reason = event.get("reason", "Stock reservation failed")
    if not order_id:
        logger.warning("Received stock_reservation_failed event without order_id", extra={"event": event})
        return

    logger.warning(f"Stock reservation failed for order {order_id}: {reason}")
    await _fail_order(order_id, reason)


@router.subscriber("balance_reservation_failed", group_id="order_service")
async def handle_balance_reservation_failed(event: dict) -> None:
    """
    Обработчик события неудачной резервации баланса - отменяет заказ.
    
    Args:
        event: Словарь с полями order_id, reason
    """
    order_id = event.get("order_id")
    reason = event.get("reason", "Balance reservation failed")
    if not order_id:
        logger.warning("Received balance_reservation_failed event without order_id", extra={"event": event})
        return

    logger.warning(f"Balance reservation failed for order {order_id}: {reason}")
    await _fail_order(order_id, reason)


async def _check_and_confirm_order(order_id: int) -> None:
    """Проверяет все резервации и подтверждает заказ если все успешно."""
    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                order_service = container.order_service()
                saga_repo = container.saga_reservation_repository()
                row = await saga_repo.get_by_order_id(order_id)
                if not row or not row.stock_done or not row.balance_done:
                    return
                order = await order_service.orders_repository.get_order_by_id(order_id)
                if order and order.status == OrderStatus.PENDING:
                    await order_service.confirm_order(order_id)
                    logger.info(f"Order {order_id} confirmed successfully")
                await saga_repo.delete_by_order_id(order_id)
                await session.commit()
    except Exception as e:
        logger.error(f"Error confirming order {order_id}: {e}", exc_info=True)
        raise


async def _fail_order(order_id: int, reason: str) -> None:
    """Отменяет заказ и запускает компенсацию."""
    logger.info(f"Failing order {order_id}, reason: {reason}")
    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                order_service = container.order_service()
                saga_repo = container.saga_reservation_repository()
                order = await order_service.orders_repository.get_order_by_id(order_id)
                if order and order.status == OrderStatus.PENDING:
                    await order_service.fail_order(order_id, reason)
                    logger.info(f"Order {order_id} failed successfully")
                await saga_repo.delete_by_order_id(order_id)
                await session.commit()
    except Exception as e:
        logger.error(f"Error failing order {order_id}: {e}", exc_info=True)
        raise

