from app.exceptions import (
    CannotMakeOrderWithoutAddress,
    CannotMakeOrderWithoutItems,
    NotEnoughProductsInStock,
    UserIsNotPresentException,
    NotEnoughBalanceToMakeOrder
)
from app.schemas.orders import SCartItemForOrder
from app.services.user_client import get_user_delivery_address, get_user_balance
from app.services.product_client import get_stock_by_ids
from shared import get_logger

logger = get_logger(__name__)


class OrderValidator:
    """
    Валидатор для проверки условий создания заказа.

    Проверяет наличие адреса доставки, товаров в корзине,
    достаточность остатков на складе и баланса пользователя.
    """

    async def validate_order(self,
                             user_id: int,
                             cart_items: list[SCartItemForOrder],
                             total_cost: int) -> None:
        """
        Валидирует все условия для создания заказа.

        Args:
            user_id: ID пользователя
            cart_items: Список товаров в корзине
            total_cost: Общая стоимость заказа

        Raises:
            CannotMakeOrderWithoutAddress: Если у пользователя нет адреса доставки
            CannotMakeOrderWithoutItems: Если корзина пуста
            NotEnoughProductsInStock: Если недостаточно товаров на складе
            UserIsNotPresentException: Если пользователь не найден
            NotEnoughBalanceToMakeOrder: Если недостаточно баланса
        """
        logger.debug(f"Validating order for user {user_id}, items: {len(cart_items)}, total: {total_cost}")
        try:
            await self._validate_address(user_id)
            await self._validate_cart_not_empty(cart_items)
            await self._validate_stock(cart_items)
            await self._validate_balance(user_id, total_cost)
            logger.debug(f"Order validation passed for user {user_id}")
        except Exception as e:
            logger.warning(f"Order validation failed for user {user_id}: {e}")
            raise

    async def _validate_address(self, user_id: int) -> None:
        """
        Проверяет наличие адреса доставки у пользователя.

        Args:
            user_id: ID пользователя

        Raises:
            CannotMakeOrderWithoutAddress: Если адрес не указан
        """
        delivery_address = await get_user_delivery_address(user_id)
        if not delivery_address:
            logger.warning(f"User {user_id} has no delivery address")
            raise CannotMakeOrderWithoutAddress
        logger.debug(f"Address validation passed for user {user_id}")

    async def _validate_cart_not_empty(self, cart_items: list[SCartItemForOrder]) -> None:
        """
        Проверяет, что корзина не пуста.

        Args:
            cart_items: Список товаров в корзине

        Raises:
            CannotMakeOrderWithoutItems: Если корзина пуста
        """
        if not cart_items:
            logger.warning("Cart is empty")
            raise CannotMakeOrderWithoutItems
        logger.debug(f"Cart validation passed: {len(cart_items)} items")

    async def _validate_stock(self, cart_items: list[SCartItemForOrder]) -> None:
        """
        Проверяет достаточность остатков товаров на складе.

        Args:
            cart_items: Список товаров в корзине

        Raises:
            NotEnoughProductsInStock: Если недостаточно товаров на складе
        """
        product_ids = [item.product_id for item in cart_items]
        stock_items = await get_stock_by_ids(product_ids)
        logger.debug(f"Stock data retrieved for {len(product_ids)} products")

        for item in cart_items:
            available = stock_items.get(item.product_id, 0)
            if item.quantity > available:
                logger.warning(f"Insufficient stock for product {item.product_id}: requested {item.quantity}, available {available}")
                raise NotEnoughProductsInStock
        logger.debug("Stock validation passed")

    async def _validate_balance(self, user_id: int, total_cost: int) -> None:
        """
        Проверяет достаточность баланса пользователя для оплаты заказа.

        Args:
            user_id: ID пользователя
            total_cost: Общая стоимость заказа

        Raises:
            UserIsNotPresentException: Если пользователь не найден
            NotEnoughBalanceToMakeOrder: Если недостаточно баланса
        """
        current_balance = await get_user_balance(user_id)
        if current_balance is None:
            logger.warning(f"User {user_id} not found")
            raise UserIsNotPresentException

        if current_balance < total_cost:
            logger.warning(f"Insufficient balance for user {user_id}: current {current_balance}, required {total_cost}")
            raise NotEnoughBalanceToMakeOrder
        logger.debug(f"Balance validation passed for user {user_id}: balance {current_balance}, cost {total_cost}")

