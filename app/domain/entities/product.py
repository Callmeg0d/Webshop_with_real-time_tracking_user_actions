from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ProductItem:
    """Domain entity для товаров."""
    product_id: int | None  # None при создании, int после сохранения в БД
    name: str
    description: str
    price: int
    product_quantity: int
    image: Optional[int]
    features: Optional[dict[str, Any]]
    category_id: int