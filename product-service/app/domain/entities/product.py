from dataclasses import dataclass


@dataclass
class ProductItem:
    """Domain entity для товаров."""
    product_id: int | None  # None при создании, int после сохранения в БД
    name: str
    description: str
    price: int
    product_quantity: int
    image: int | None
    features: dict[str, str] | None
    category_id: int

