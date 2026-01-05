from faststream.kafka import KafkaRouter
from shared import get_logger

from app.database import async_session_maker
from app.core.container import Container
from app.constants import ORDER_STATUS_PENDING, ORDER_STATUS_CONFIRMED, ORDER_STATUS_FAILED

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


# Храним состояние резервации для каждого заказа
# todo: использовать Redis или БД
_order_reservations: dict[int, dict[str, bool]] = {}


@router.subscriber("stock_reserved", group_id="order_service")
async def handle_stock_reserved(event: dict) -> None:
    """
    Обработчик события успешной резервации товаров.
    
    Args:
        event: Словарь с полями order_id
    """
    order_id = event.get("order_id")
    if not order_id:
        logger.warning("Received stock_reserved event without order_id", extra={"event": event})
        return

    logger.info(f"Processing stock reservation for order {order_id}")
    
    try:
        # Проверяем статус заказа для идемпотентности
        async with async_session_maker() as session:
            order_service = container.order_service(db=session)
            order = await order_service.orders_repository.get_order_by_id(order_id)

            # Если заказ уже подтвержден или отменен, игнорируем событие
            if not order or order.status != ORDER_STATUS_PENDING:
                logger.debug(
                    f"Order {order_id} already processed (status: {order.status if order else 'not found'})")
                return
    
        # Отмечаем резервацию товаров
        if order_id not in _order_reservations:
            _order_reservations[order_id] = {"stock": False, "balance": False}
        _order_reservations[order_id]["stock"] = True

        logger.info(f"Stock reservation confirmed for order {order_id}")
        # Проверяем, все ли резервации завершены
        await _check_and_confirm_order(order_id)

    except Exception as e:
        logger.error(f"Error processing stock reservation for order {order_id}: {e}", exc_info=True)
        raise


@router.subscriber("balance_reserved", group_id="order_service")
async def handle_balance_reserved(event: dict) -> None:
    """
    Обработчик события успешной резервации баланса.
    
    Args:
        event: Словарь с полями order_id
    """
    order_id = event.get("order_id")
    if not order_id:
        logger.warning("Received balance_reserved event without order_id", extra={"event": event})
        return

    logger.info(f"Processing balance reservation for order {order_id}")
    
    try:
        # Проверяем статус заказа для идемпотентности
        async with async_session_maker() as session:
            order_service = container.order_service(db=session)
            order = await order_service.orders_repository.get_order_by_id(order_id)

            # Если заказ уже подтвержден или отменен, игнорируем событие
            if not order or order.status != ORDER_STATUS_PENDING:
                logger.debug(
                    f"Order {order_id} already processed (status: {order.status if order else 'not found'})")
                return

        # Отмечаем резервацию баланса
        if order_id not in _order_reservations:
            _order_reservations[order_id] = {"stock": False, "balance": False}
        _order_reservations[order_id]["balance"] = True

        logger.info(f"Balance reservation confirmed for order {order_id}")
        # Проверяем, все ли резервации завершены
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
    reservations = _order_reservations.get(order_id)
    if not reservations:
        logger.warning(f"No reservations found for order {order_id}")
        return
    
    # Если обе резервации успешны
    if reservations.get("stock") and reservations.get("balance"):
        logger.info(f"All reservations completed for order {order_id}, confirming order")
        try:
            async with async_session_maker() as session:
                order_service = container.order_service(db=session)

                # Идемпотентность: проверяем статус перед подтверждением
                order = await order_service.orders_repository.get_order_by_id(order_id)
                if order and order.status == ORDER_STATUS_PENDING:
                    await order_service.confirm_order(order_id)
                    logger.info(f"Order {order_id} confirmed successfully")

            # Очищаем состояние
            _order_reservations.pop(order_id, None)

        except Exception as e:
            logger.error(f"Error confirming order {order_id}: {e}", exc_info=True)
            raise


async def _fail_order(order_id: int, reason: str) -> None:
    """Отменяет заказ и запускает компенсацию."""
    logger.info(f"Failing order {order_id}, reason: {reason}")
    try:
        async with async_session_maker() as session:
            order_service = container.order_service(db=session)

            # Идемпотентность: проверяем статус перед отменой
            order = await order_service.orders_repository.get_order_by_id(order_id)
            if order and order.status == ORDER_STATUS_PENDING:
                await order_service.fail_order(order_id, reason)
                logger.info(f"Order {order_id} failed successfully")

        # Очищаем состояние
        _order_reservations.pop(order_id, None)

    except Exception as e:
        logger.error(f"Error failing order {order_id}: {e}", exc_info=True)
        raise

