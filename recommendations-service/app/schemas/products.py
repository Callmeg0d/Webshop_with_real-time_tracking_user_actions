from typing import TypedDict

# Входящий продукт из Kafka
IncomingProduct = dict[str, str | int | dict[str, str] | None]


class ProductPayload(TypedDict):
    """Payload товара для Qdrant"""
    product_id: int
    name: str
    description: str
    price: int
    product_quantity: int
    image: str
    features: dict[str, str]
    category_id: int


class ProductCreatedRequest(TypedDict, total=False):
    """Тело сообщения из топика product_created"""
    product: IncomingProduct


class ProductRemovedRequest(TypedDict, total=False):
    """Тело сообщения из топика product_removed"""
    product: IncomingProduct


class ProductUpdatedRequest(TypedDict, total=False):
    """Тело сообщения из топика product_updated"""
    product: IncomingProduct
