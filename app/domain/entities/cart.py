from dataclasses import dataclass


@dataclass
class CartItem:
    """Domain entity для корзины товаров."""
    cart_id: int | None  # None при создании, int после сохранения в БД
    user_id: int
    product_id: int
    quantity: int
    total_cost: int