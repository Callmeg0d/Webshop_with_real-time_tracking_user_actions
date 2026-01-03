from faststream.kafka import KafkaRouter

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_balance_reserved, publish_balance_reservation_failed

router = KafkaRouter()
container = Container()


# Отслеживание обработанных заказов для идемпотентности
# todo: использовать Redis или БД
_processed_orders: set[int] = set()
# Отслеживание компенсаций
# todo: использовать Redis или БД
_compensations: set[int] = set()


@router.subscriber("order_processing_started", group_id="user_service")
async def handle_order_processing_started(event: dict) -> None:
    """
    Обработчик события начала обработки заказа - резервирует баланс.
    
    Args:
        event: Словарь с полями order_id, user_id, total_cost
    """
    order_id = event.get("order_id")
    user_id = event.get("user_id")
    total_cost = event.get("total_cost")
    
    if not order_id or not user_id or not total_cost:
        return
    
    # Идемпотентность: проверяем, был ли уже обработан этот заказ
    if order_id in _processed_orders:
        # Если заказ уже обработан, просто подтверждаем резервацию
        await publish_balance_reserved(order_id)
        return
    
    try:
        async with async_session_maker() as session:
            user_service = container.user_service(db=session)
            
            # Проверяем баланс
            current_balance = await user_service.get_balance(user_id)
            if current_balance is None:
                await publish_balance_reservation_failed(
                    order_id,
                    f"User {user_id} not found"
                )
                return
            
            if current_balance < total_cost:
                await publish_balance_reservation_failed(
                    order_id,
                    f"Insufficient balance: {current_balance} < {total_cost}"
                )
                return
            
            # Резервируем баланс (списываем)
            await user_service.decrease_balance(user_id, total_cost)
            
            # Баланс успешно зарезервирован
            _processed_orders.add(order_id)
            await publish_balance_reserved(order_id)
            
    except Exception as e:
        await publish_balance_reservation_failed(order_id, str(e))


@router.subscriber("balance_increase", group_id="user_service")
async def handle_balance_increase(request: dict) -> None:
    """
    Обработчик события возврата баланса (компенсация).
    
    Args:
        request: Словарь с полями order_id, user_id и amount
    """
    order_id = request.get("order_id")
    user_id = request.get("user_id")
    amount = request.get("amount")
    
    if not order_id or not user_id or not amount:
        return
    
    # Идемпотентность: проверяем, была ли уже выполнена компенсация
    if order_id in _compensations:
        return
    _compensations.add(order_id)
    
    async with async_session_maker() as session:
        user_service = container.user_service(db=session)
        await user_service.increase_balance(user_id, amount)