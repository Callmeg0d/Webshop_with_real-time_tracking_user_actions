from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderSagaReservationItem:
    """Состояние резерваций саги по заказу."""
    order_id: int
    stock_done: bool
    balance_done: bool
    updated_at: datetime | None = None
