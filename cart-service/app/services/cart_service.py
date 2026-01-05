from sqlalchemy.ext.asyncio import AsyncSession
from shared import get_logger

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.cart import CartItem
from app.domain.interfaces.carts_repo import ICartsRepository
from app.schemas.carts import SCartItem, SCartItemWithProduct
from app.services.product_client import get_product
from app.exceptions import CannotHaveLessThan1Product, NeedToHaveAProductToIncreaseItsQuantity

logger = get_logger(__name__)


class CartService:
    def __init__(
            self,
            carts_repository: ICartsRepository,
            db: AsyncSession
    ):
        """
        Сервис для управления корзиной покупок пользователя

        Args:
            carts_repository: Репозиторий для работы с корзиной в БД
            db: Асинхронная сессия базы данных
        """
        self.cart_repository = carts_repository
        self.db = db

    async def get_user_cart(self, user_id: int) -> list[SCartItem]:
        """
        Получает все товары в корзине пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список товаров в корзине
        """
        logger.debug(f"Fetching cart for user {user_id}")
        try:
            user_cart = await self.cart_repository.get_cart_items(user_id=user_id)
            logger.debug(f"Found {len(user_cart)} items in cart for user {user_id}")
            return user_cart
        except Exception as e:
            logger.error(f"Error fetching cart for user {user_id}: {e}", exc_info=True)
            raise

    async def clear_user_cart(self, user_id: int) -> None:
        """
        Очищает всю корзину пользователя

        Args:
            user_id: ID пользователя
        """
        logger.info(f"Clearing cart for user {user_id}")
        try:
            async with UnitOfWork(self.db):
                await self.cart_repository.clear_cart(user_id=user_id)
            logger.info(f"Cart cleared successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing cart for user {user_id}: {e}", exc_info=True)
            raise

    async def get_total_cost(self, user_id: int) -> int:
        """
        Рассчитывает общую стоимость всех товаров в корзине

        Args:
            user_id: ID пользователя

        Returns:
            Общая стоимость корзины
        """
        logger.debug(f"Calculating total cost for user {user_id}")
        try:
            total_cost = await self.cart_repository.get_total_cost(user_id=user_id)
            logger.debug(f"Total cost for user {user_id}: {total_cost}")
            return total_cost
        except Exception as e:
            logger.error(f"Error calculating total cost for user {user_id}: {e}", exc_info=True)
            raise

    async def add_to_cart(
            self,
            user_id: int,
            product_id: int,
            quantity: int
    ) -> None:
        """
        Добавляет товар в корзину или обновляет количество существующего.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity: Количество для добавления
        """
        logger.info(f"Adding product {product_id} to cart for user {user_id}, quantity: {quantity}")
        try:
            # Получаем информацию о продукте из product-service
            product = await get_product(product_id)
            product_price = product["price"]
            logger.debug(f"Product {product_id} price: {product_price}")

            # Проверяем, есть ли уже этот товар в корзине
            existing_item = await self.cart_repository.get_cart_item_by_id(
                user_id=user_id,
                product_id=product_id
            )

            async with UnitOfWork(self.db):
                if existing_item:
                    # Обновляем количество
                    logger.debug(f"Updating existing cart item for product {product_id}")
                    await self.cart_repository.update_cart_item(
                        user_id=user_id,
                        product_id=product_id,
                        quantity_add=quantity,
                        cost_add=product_price * quantity
                    )
                else:
                    # Добавляем новый товар
                    logger.debug(f"Adding new cart item for product {product_id}")
                    await self.cart_repository.add_cart_item(
                        user_id=user_id,
                        product_id=product_id,
                        quantity=quantity,
                        total_cost=product_price * quantity
                    )
            logger.info(f"Product {product_id} added to cart successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error adding product {product_id} to cart for user {user_id}: {e}", exc_info=True)
            raise

    async def remove_cart_item(self, user_id: int, product_id: int) -> None:
        """
        Удаляет товар из корзины

        Args:
            user_id: ID пользователя
            product_id: ID товара для удаления
        """
        logger.info(f"Removing product {product_id} from cart for user {user_id}")
        try:
            async with UnitOfWork(self.db):
                await self.cart_repository.remove_cart_item(
                    user_id=user_id,
                    product_id=product_id,
                )
            logger.info(f"Product {product_id} removed from cart successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error removing product {product_id} from cart for user {user_id}: {e}", exc_info=True)
            raise

    async def get_cart_items_with_products(self, user_id: int) -> list[SCartItemWithProduct]:
        """
        Получает товары корзины с подробной информацией о товарах.

        Args:
            user_id: ID пользователя

        Returns:
            Список товаров с детальной информацией
        """
        logger.debug(f"Fetching cart items with products for user {user_id}")
        try:
            cart_items = await self.cart_repository.get_cart_items(user_id=user_id)
            logger.debug(f"Found {len(cart_items)} items in cart for user {user_id}")
            
            # Получаем информацию о продуктах из product-service
            result = []
            for item in cart_items:
                try:
                    product = await get_product(item.product_id)
                    result.append(SCartItemWithProduct(
                        product_id=item.product_id,
                        name=product["name"],
                        description=product["description"],
                        price=product["price"],
                        quantity=item.quantity,
                        total_cost=item.total_cost,
                        product_quantity=product["product_quantity"]
                    ))
                except Exception as e:
                    # Если продукт не найден, пропускаем его
                    logger.warning(f"Product {item.product_id} not found, skipping: {e}")
                    continue
            
            logger.debug(f"Returning {len(result)} cart items with product info for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error fetching cart items with products for user {user_id}: {e}", exc_info=True)
            raise

    async def update_quantity(self, user_id: int, product_id: int, quantity: int) -> int:
        """
        Обновляет количество конкретного товара в корзине

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity: Новое количество товара

        Returns:
            Обновленная общая стоимость товара
        """
        logger.info(f"Updating quantity for product {product_id} in cart for user {user_id}, new quantity: {quantity}")
        try:
            if quantity < 1:
                logger.warning(f"Invalid quantity {quantity} for product {product_id}")
                raise CannotHaveLessThan1Product

            existing_item = await self.cart_repository.get_cart_item_by_id(
                user_id=user_id,
                product_id=product_id
            )
            
            if not existing_item:
                logger.warning(f"Product {product_id} not found in cart for user {user_id}")
                raise NeedToHaveAProductToIncreaseItsQuantity

            # Получаем цену продукта из product-service
            product = await get_product(product_id)
            product_price = product["price"]
            logger.debug(f"Product {product_id} price: {product_price}")

            async with UnitOfWork(self.db):
                total_cost = await self.cart_repository.update_quantity(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    price=product_price
                )
            logger.info(f"Quantity updated successfully for product {product_id}, total_cost: {total_cost}")
            return total_cost
        except (CannotHaveLessThan1Product, NeedToHaveAProductToIncreaseItsQuantity):
            raise
        except Exception as e:
            logger.error(f"Error updating quantity for product {product_id} in cart for user {user_id}: {e}", exc_info=True)
            raise

    async def get_cart_item_by_id(self, user_id: int, product_id: int) -> CartItem | None:
        """
        Находит конкретный товар в корзине пользователя по id

        Args:
            user_id: ID пользователя
            product_id: ID товара

        Returns:
            Найденный товар или None если не найден
        """
        return await self.cart_repository.get_cart_item_by_id(user_id=user_id, product_id=product_id)

