from faststream.kafka import KafkaRouter
from shared import get_logger

from app.database import async_session_maker
from app.core.container import Container
from app.messaging.publisher import publish_stock_reserved, publish_stock_reservation_failed

router = KafkaRouter()
container = Container()
logger = get_logger(__name__)


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
        logger.warning("Received order_processing_started event without order_id or order_items", extra={"event": event})
        return
    
    logger.info(f"Processing stock reservation for order {order_id}, items: {len(order_items)}")
    
    # Идемпотентность: проверяем, был ли уже обработан этот заказ
    if order_id in _processed_orders:
        logger.debug(f"Order {order_id} already processed, confirming reservation")
        await publish_stock_reserved(order_id)
        return
    
    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                product_service = container.product_service()
                
                # Резервируем товары для каждого элемента заказа
                for item in order_items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity")
                    
                    if not product_id or not quantity:
                        logger.warning(f"Skipping invalid item in order {order_id}: {item}")
                        continue
                    
                    logger.debug(f"Reserving product {product_id}, quantity {quantity} for order {order_id}")
                    
                    # Проверяем наличие товара и достаточность остатков
                    stock = await product_service.get_stock_by_ids([product_id])
                    available = stock.get(product_id, 0)
                    
                    if available < quantity:
                        logger.warning(f"Insufficient stock for product {product_id}: available {available}, required {quantity}")
                        await publish_stock_reservation_failed(
                            order_id, 
                            f"Insufficient stock for product {product_id}"
                        )
                        return
                    
                    # Уменьшаем остатки
                    await product_service.decrease_stock(product_id, quantity)
                    logger.debug(f"Stock decreased for product {product_id}, quantity {quantity}")
                
                # Все товары успешно зарезервированы
                _processed_orders.add(order_id)
                await publish_stock_reserved(order_id)
                logger.info(f"Stock reservation completed successfully for order {order_id}")
            
    except Exception as e:
        logger.error(f"Error processing stock reservation for order {order_id}: {e}", exc_info=True)
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
        logger.warning("Received stock_increase event without required fields", extra={"request": request})
        return
    
    logger.info(f"Processing stock increase (compensation) for order {order_id}, product {product_id}, quantity {quantity}")
    
    # Идемпотентность: проверяем, была ли уже выполнена компенсация
    compensation_key = (order_id, product_id)
    if compensation_key in _compensations:
        logger.debug(f"Compensation already processed for order {order_id}, product {product_id}")
        return
    _compensations.add(compensation_key)
    
    try:
        async with async_session_maker() as session:
            with container.db.override(session):
                product_service = container.product_service()
                await product_service.increase_stock(product_id, quantity)
        logger.info(f"Stock increase (compensation) completed for order {order_id}, product {product_id}")
    except Exception as e:
        logger.error(f"Error processing stock increase for order {order_id}, product {product_id}: {e}", exc_info=True)
        raise