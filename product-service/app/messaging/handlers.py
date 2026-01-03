from faststream.kafka import KafkaRouter

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_stock_reserved, publish_stock_reservation_failed

router = KafkaRouter()
container = Container()


# Отслеживание обработанных заказов для идемпотентности
# todo: использовать Redis или БД
_processed_orders: set[int] = set()
# Отслеживание компенсаций
# todo: использовать Redis или БД
_compensations: set[tuple[int, int]] = set()


@router.subscriber("order_processing_started", group_id="product_service")
async def handle_order_processing_started(event: dict) -> None:
    """
    Обработчик события начала обработки заказа - резервирует товары.
    
    Args:
        event: Словарь с полями order_id, order_items
    """
    order_id = event.get("order_id")
    order_items = event.get("order_items", [])
    
    if not order_id or not order_items:
        return
    
    # Идемпотентность: проверяем, был ли уже обработан этот заказ
    if order_id in _processed_orders:
        # Если заказ уже обработан, просто подтверждаем резервацию
        await publish_stock_reserved(order_id)
        return
    
    try:
        async with async_session_maker() as session:
            product_service = container.product_service(db=session)
            
            # Резервируем товары для каждого элемента заказа
            for item in order_items:
                product_id = item.get("product_id")
                quantity = item.get("quantity")
                
                if not product_id or not quantity:
                    continue
                
                # Проверяем наличие товара и достаточность остатков
                stock = await product_service.get_stock_by_ids([product_id])
                available = stock.get(product_id, 0)
                
                if available < quantity:
                    await publish_stock_reservation_failed(
                        order_id, 
                        f"Insufficient stock for product {product_id}"
                    )
                    return
                
                # Уменьшаем остатки
                await product_service.decrease_stock(product_id, quantity)
            
            # Все товары успешно зарезервированы
            _processed_orders.add(order_id)
            await publish_stock_reserved(order_id)
            
    except Exception as e:
        await publish_stock_reservation_failed(order_id, str(e))


@router.subscriber("stock_increase", group_id="product_service")
async def handle_stock_increase(request: dict) -> None:
    """
    Обработчик события возврата товаров (компенсация).
    
    Args:
        request: Словарь с полями order_id, product_id и quantity
    """
    order_id = request.get("order_id")
    product_id = request.get("product_id")
    quantity = request.get("quantity")
    
    if not order_id or not product_id or not quantity:
        return
    
    # Идемпотентность: проверяем, была ли уже выполнена компенсация
    compensation_key = (order_id, product_id)
    if compensation_key in _compensations:
        return
    _compensations.add(compensation_key)
    
    async with async_session_maker() as session:
        product_service = container.product_service(db=session)
        await product_service.increase_stock(product_id, quantity)