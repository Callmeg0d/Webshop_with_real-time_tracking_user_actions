from dataclasses import dataclass
from datetime import date
from typing import List, Dict


@dataclass
class OrderItem:
    order_id: int | None  # None при создании, int после сохранения в БД
    user_id: int
    created_at: date
    status: str
    delivery_address: str
    order_items: List[Dict[str, str | int]]
    total_cost: int