from dataclasses import dataclass
from typing import Literal


@dataclass
class CartItem:
    """Domain entity для корзины товаров."""
    cart_id: int | None  # None при создании, int после сохранения в БД
    user_id: int
    product_id: int
    quantity: int
    total_cost: int


@dataclass
class CartOperationResult:
    """ DTO для результата операции с корзиной"""
    action: Literal["added", "updated"]
    product_id: int
    quantity_added: int
    total_cost: float
    cart_total: float

