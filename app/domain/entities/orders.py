from dataclasses import dataclass
from datetime import date


@dataclass
class OrderItem:
    """Domain entity для заказов."""
    user_id: int
    created_at: date
    status: str
    delivery_address: str
    order_items: list[dict[str, str | int]]
    total_cost: int
    order_id: int | None = None  # None при создании, int после сохранения в БД