from typing import Protocol, List

from app.domain.entities.orders import OrderItem


class IOrdersRepository(Protocol):
    async def create_order(self, order: OrderItem) -> OrderItem:
        ...

    async def get_by_user_id(self, user_id: int) -> List[OrderItem]:
        ...

