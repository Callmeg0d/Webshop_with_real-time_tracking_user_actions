from typing import Protocol

from app.domain.entities.orders import OrderItem


class IOrdersRepository(Protocol):
    async def create_order(self, order: OrderItem) -> OrderItem:
        ...

    async def update_order_status(self, order_id: int, status: str) -> None:
        ...

    async def get_order_by_id(self, order_id: int) -> OrderItem | None:
        ...

    async def get_by_user_id(self, user_id: int) -> list[OrderItem]:
        ...

