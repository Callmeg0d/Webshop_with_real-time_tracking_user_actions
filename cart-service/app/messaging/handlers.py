from faststream.kafka import KafkaRouter

from app.database import async_session_maker
from app.repositories.carts_repository import CartsRepository
from app.core.unit_of_work import UnitOfWork

router = KafkaRouter()


# Отслеживание обработанных заказов для идемпотентности
# todo: использовать Redis или БД
_processed_orders: set[int] = set()


@router.subscriber("order_confirmed", group_id="cart_service")
async def handle_order_confirmed(order: dict) -> None:
    """
    Обработчик события подтверждения заказа - очищает корзину пользователя.
    
    Args:
        order: Словарь с данными заказа
    """
    order_id = order.get("order_id")
    user_id = order.get("user_id")
    
    if not order_id or not user_id:
        return
    
    # Идемпотентность: проверяем, был ли уже обработан этот заказ
    if order_id in _processed_orders:
        return
    
    async with async_session_maker() as session:
        carts_repository = CartsRepository(session)
        
        async with UnitOfWork(session):
            await carts_repository.clear_cart(user_id=user_id)
            _processed_orders.add(order_id)

