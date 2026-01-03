from faststream.kafka import KafkaRouter

from app.database import async_session_maker
from app.core.container import Container
from app.constants import ORDER_STATUS_PENDING, ORDER_STATUS_CONFIRMED, ORDER_STATUS_FAILED

router = KafkaRouter()
container = Container()


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
        return
    
    # Проверяем статус заказа для идемпотентности
    async with async_session_maker() as session:
        order_service = container.order_service(db=session)
        order = await order_service.orders_repository.get_order_by_id(order_id)
        
        # Если заказ уже подтвержден или отменен, игнорируем событие
        if not order or order.status != ORDER_STATUS_PENDING:
            return
    
    # Отмечаем резервацию товаров
    if order_id not in _order_reservations:
        _order_reservations[order_id] = {"stock": False, "balance": False}
    _order_reservations[order_id]["stock"] = True
    
    # Проверяем, все ли резервации завершены
    await _check_and_confirm_order(order_id)


@router.subscriber("balance_reserved", group_id="order_service")
async def handle_balance_reserved(event: dict) -> None:
    """
    Обработчик события успешной резервации баланса.
    
    Args:
        event: Словарь с полями order_id
    """
    order_id = event.get("order_id")
    if not order_id:
        return
    
    # Проверяем статус заказа для идемпотентности
    async with async_session_maker() as session:
        order_service = container.order_service(db=session)
        order = await order_service.orders_repository.get_order_by_id(order_id)
        
        # Если заказ уже подтвержден или отменен, игнорируем событие
        if not order or order.status != ORDER_STATUS_PENDING:
            return
    
    # Отмечаем резервацию баланса
    if order_id not in _order_reservations:
        _order_reservations[order_id] = {"stock": False, "balance": False}
    _order_reservations[order_id]["balance"] = True
    
    # Проверяем, все ли резервации завершены
    await _check_and_confirm_order(order_id)


@router.subscriber("stock_reservation_failed", group_id="order_service")
async def handle_stock_reservation_failed(event: dict) -> None:
    """
    Обработчик события неудачной резервации товаров - отменяет заказ.
    
    Args:
        event: Словарь с полями order_id, reason
    """
    order_id = event.get("order_id")
    if not order_id:
        return
    
    await _fail_order(order_id, event.get("reason", "Stock reservation failed"))


@router.subscriber("balance_reservation_failed", group_id="order_service")
async def handle_balance_reservation_failed(event: dict) -> None:
    """
    Обработчик события неудачной резервации баланса - отменяет заказ.
    
    Args:
        event: Словарь с полями order_id, reason
    """
    order_id = event.get("order_id")
    if not order_id:
        return
    
    await _fail_order(order_id, event.get("reason", "Balance reservation failed"))


async def _check_and_confirm_order(order_id: int) -> None:
    """Проверяет все резервации и подтверждает заказ если все успешно."""
    reservations = _order_reservations.get(order_id)
    if not reservations:
        return
    
    # Если обе резервации успешны
    if reservations.get("stock") and reservations.get("balance"):
        async with async_session_maker() as session:
            order_service = container.order_service(db=session)
            
            # Идемпотентность: проверяем статус перед подтверждением
            order = await order_service.orders_repository.get_order_by_id(order_id)
            if order and order.status == ORDER_STATUS_PENDING:
                await order_service.confirm_order(order_id)
        
        # Очищаем состояние
        _order_reservations.pop(order_id, None)


async def _fail_order(order_id: int, reason: str) -> None:
    """Отменяет заказ и запускает компенсацию."""
    async with async_session_maker() as session:
        order_service = container.order_service(db=session)
        
        # Идемпотентность: проверяем статус перед отменой
        order = await order_service.orders_repository.get_order_by_id(order_id)
        if order and order.status == ORDER_STATUS_PENDING:
            await order_service.fail_order(order_id, reason)
    
    # Очищаем состояние
    _order_reservations.pop(order_id, None)

