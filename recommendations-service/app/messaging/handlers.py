from faststream.kafka import KafkaRouter

from app.schemas.products import (
    IncomingProduct,
    ProductCreatedRequest,
    ProductRemovedRequest,
    ProductUpdatedRequest,
)
from app.store import product_index_service

router: KafkaRouter = KafkaRouter()


def get_product_from_request(request: dict | None, key: str = "product") -> IncomingProduct | None:
    """Извлекает и валидирует продукт из тела сообщения Kafka. Возвращает None, если невалидно"""
    if not request or not isinstance(request, dict):
        return None
    product = request.get(key)
    if not product or not isinstance(product, dict) or not isinstance(product.get("product_id"), int):
        return None
    return product


@router.subscriber("product_created", group_id="recommendation_service")
async def handle_product_created(request: ProductCreatedRequest) -> None:
    product = get_product_from_request(request)
    if product is None:
        return
    await product_index_service.index_product(product)


@router.subscriber("product_updated", group_id="recommendation_service")
async def handle_product_updated(request: ProductUpdatedRequest) -> None:
    product = get_product_from_request(request)
    if product is None:
        return
    await product_index_service.index_product(product)


@router.subscriber("product_removed", group_id="recommendation_service")
async def handle_product_removed(request: ProductRemovedRequest) -> None:
    product = get_product_from_request(request)
    if product is None:
        return
    await product_index_service.remove_product(product["product_id"])

