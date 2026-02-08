from typing import Final


class OrderStatus:
    """Статусы заказа."""
    PENDING: Final[str] = "Pending"
    CONFIRMED: Final[str] = "Confirmed"
    FAILED: Final[str] = "Failed"
    ARRIVING: Final[str] = "Arriving"
