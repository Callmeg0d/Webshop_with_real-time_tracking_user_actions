from abc import ABC, abstractmethod
from app.domain.entities.cart import CartOperationResult
from app.domain.interfaces.carts_repo import ICartsRepository


class CartOperationStrategy(ABC):
    """Абстрактная стратегия операции с корзиной"""

    @abstractmethod
    async def execute(
            self,
            user_id: int,
            product_id: int,
            quantity: int,
            product_price: int
    ) -> CartOperationResult:
        pass


class AddCartItemStrategy(CartOperationStrategy):
    """Стратегия добавления нового товара"""

    def __init__(self, repository: ICartsRepository):
        self.repository = repository

    async def execute(self, user_id: int, product_id: int,
                      quantity: int, product_price: int) -> CartOperationResult:
        total_cost = product_price * quantity

        await self.repository.add_cart_item(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_cost=total_cost
        )

        cart_total = await self.repository.get_total_cost(user_id)

        return CartOperationResult(
            action="added",
            product_id=product_id,
            quantity_added=quantity,
            total_cost=total_cost,
            cart_total=cart_total
        )


class UpdateCartItemStrategy(CartOperationStrategy):
    """Стратегия обновления существующего товара"""

    def __init__(self, repository: ICartsRepository):
        self.repository = repository

    async def execute(self, user_id: int, product_id: int,
                      quantity: int, product_price: int) -> CartOperationResult:
        total_cost = product_price * quantity

        await self.repository.update_cart_item(
            user_id=user_id,
            product_id=product_id,
            quantity_add=quantity,
            cost_add=total_cost
        )

        cart_total = await self.repository.get_total_cost(user_id)

        return CartOperationResult(
            action="updated",
            product_id=product_id,
            quantity_added=quantity,
            total_cost=total_cost,
            cart_total=cart_total
        )