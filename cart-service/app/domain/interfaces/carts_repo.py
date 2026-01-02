from typing import Protocol

from app.domain.entities.cart import CartItem
from app.schemas.carts import SCartItem


class ICartsRepository(Protocol):

    async def clear_cart(self, user_id: int) -> None:
        ...

    async def get_cart_items(self, user_id: int) -> list[SCartItem]:
        ...

    async def get_total_cost(self, user_id: int) -> int:
        ...

    async def update_cart_item(self, user_id: int, product_id: int,
                               quantity_add: int, cost_add: int) -> None:
        ...

    async def add_cart_item(self, user_id: int, product_id: int,
                            quantity: int, total_cost: int) -> CartItem:
        ...

    async def remove_cart_item(self, user_id: int, product_id: int) -> None:
        ...

    async def update_quantity(self, user_id: int, product_id: int, quantity: int) -> int:
        ...

    async def get_cart_item_by_id(self, user_id: int, product_id: int) -> CartItem | None:
        ...

