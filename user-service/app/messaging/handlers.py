from faststream.kafka import KafkaRouter
from shared import get_logger

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_balance_reserved, publish_balance_reservation_failed

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


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
        logger.warning("Received order_processing_started event without required fields", extra={"event": event})
        return
    
    logger.info(f"Processing balance reservation for order {order_id}, user {user_id}, cost: {total_cost}")
    
    # Идемпотентность: проверяем, был ли уже обработан этот заказ
    if order_id in _processed_orders:
        logger.debug(f"Order {order_id} already processed, confirming reservation")
        await publish_balance_reserved(order_id)
        return
    
    try:
        async with async_session_maker() as session:
            user_service = container.user_service(db=session)
            
            # Проверяем баланс
            current_balance = await user_service.get_balance(user_id)
            if current_balance is None:
                logger.warning(f"User {user_id} not found for order {order_id}")
                await publish_balance_reservation_failed(
                    order_id,
                    f"User {user_id} not found"
                )
                return
            
            if current_balance < total_cost:
                logger.warning(f"Insufficient balance for user {user_id}: {current_balance} < {total_cost}")
                await publish_balance_reservation_failed(
                    order_id,
                    f"Insufficient balance: {current_balance} < {total_cost}"
                )
                return
            
            # Резервируем баланс (списываем)
            await user_service.decrease_balance(user_id, total_cost)
            logger.debug(f"Balance decreased for user {user_id}, amount: {total_cost}")
            
            # Баланс успешно зарезервирован
            _processed_orders.add(order_id)
            await publish_balance_reserved(order_id)
            logger.info(f"Balance reservation completed successfully for order {order_id}")
            
    except Exception as e:
        logger.error(f"Error processing balance reservation for order {order_id}: {e}", exc_info=True)
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
        logger.warning("Received balance_increase event without required fields", extra={"request": request})
        return
    
    logger.info(f"Processing balance increase (compensation) for order {order_id}, user {user_id}, amount: {amount}")
    
    # Идемпотентность: проверяем, была ли уже выполнена компенсация
    if order_id in _compensations:
        logger.debug(f"Compensation already processed for order {order_id}")
        return
    _compensations.add(order_id)
    
    try:
        async with async_session_maker() as session:
            user_service = container.user_service(db=session)
            await user_service.increase_balance(user_id, amount)
        logger.info(f"Balance increase (compensation) completed for order {order_id}, user {user_id}")
    except Exception as e:
        logger.error(f"Error processing balance increase for order {order_id}, user {user_id}: {e}", exc_info=True)
        raise