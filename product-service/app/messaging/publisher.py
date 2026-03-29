from app.domain.entities.product import ProductItem
from app.schemas.products import ProductPayload
from app.messaging.broker import broker


async def publish_stock_reserved(order_id: int) -> None:
    """Публикует событие успешной резервации товаров."""
    await broker.publish(
        message={"order_id": order_id},
        topic="stock_reserved",
    )


async def publish_stock_reservation_failed(order_id: int, reason: str) -> None:
    """Публикует событие неудачной резервации товаров."""
    await broker.publish(
        message={"order_id": order_id, "reason": reason},
        topic="stock_reservation_failed",
    )


def get_product_payload_for_qdrant(product: ProductItem) -> ProductPayload:
    if product.product_id is None:
        raise ValueError("product_id must be set before publishing")
    return ProductPayload(
        product_id=product.product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        product_quantity=product.product_quantity,
        image=product.image or "",
        features=product.features if isinstance(product.features, dict) else {},
        category_id=product.category_id,
    )


async def publish_product_added(product: ProductItem) -> None:
    payload = get_product_payload_for_qdrant(product)
    await broker.publish(message={"product": payload}, topic="product_created")


async def publish_product_removed(product: ProductItem) -> None:
    payload = get_product_payload_for_qdrant(product)
    await broker.publish(message={"product": payload}, topic="product_removed")


async def publish_product_updated(product: ProductItem) -> None:
    payload = get_product_payload_for_qdrant(product)
    await broker.publish(message={"product": payload}, topic="product_updated")