from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ShoppingCarts
from app.repositories import CartsRepository


class CartService:
    def __init__(
            self,
            cart_repository: CartsRepository,
            db: AsyncSession
    ):
        self.cart_repository = cart_repository
        self.db = db

    async def get_user_cart(self, user_id: int) -> List[dict]:
        user_cart = await self.cart_repository.get_cart_items(user_id=user_id)
        return user_cart

    async def clear_user_cart(self, user_id: int) -> None:
        await self.cart_repository.clear_cart(user_id=user_id)

    async def get_total_cost(self, user_id: int) -> float:
        total_cost = await self.cart_repository.get_total_cost(user_id=user_id)
        return total_cost

    async def update_cart_item(
            self,
            user_id: int,
            product_id: int,
            quantity_add: int,
            cost_add: float
    ) -> None:
        await self.cart_repository.update_cart_item(
            user_id=user_id,
            product_id=product_id,
            quantity_add=quantity_add,
            cost_add=cost_add
        )
        await self.db.commit()

    async def add_cart_item(self, user_id: int, product_id: int, quantity: int, total_cost: float) -> None:
        await self.cart_repository.add_cart_item(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_cost=total_cost
        )
        await self.db.commit()

    async def remove_cart_item(self, user_id: int, product_id: int) -> None:
        await self.cart_repository.remove_cart_item(
            user_id=user_id,
            product_id=product_id,
        )
        await self.db.commit()

    async def get_cart_items_with_products(self, user_id: int) -> List[dict]:
        cart_items = await self.cart_repository.get_cart_items_with_products(user_id=user_id)
        return cart_items

    async def update_quantity(self, user_id: int, product_id: int, quantity: int) -> None:
        await self.cart_repository.update_quantity(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        await self.db.commit()

    async def get_cart_item_by_id(self, user_id: int, product_id: int) -> Optional[ShoppingCarts]:
        return await self.cart_repository.get_cart_item_by_id(user_id=user_id, product_id=product_id)

