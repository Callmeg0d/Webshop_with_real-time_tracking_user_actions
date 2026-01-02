from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.cart import CartItem
from app.domain.interfaces.carts_repo import ICartsRepository
from app.schemas.carts import SCartItem, SCartItemWithProduct
from app.services.product_client import get_product
from app.exceptions import CannotHaveLessThan1Product, NeedToHaveAProductToIncreaseItsQuantity


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
        user_cart = await self.cart_repository.get_cart_items(user_id=user_id)
        return user_cart

    async def clear_user_cart(self, user_id: int) -> None:
        """
        Очищает всю корзину пользователя

        Args:
            user_id: ID пользователя
        """
        async with UnitOfWork(self.db):
            await self.cart_repository.clear_cart(user_id=user_id)

    async def get_total_cost(self, user_id: int) -> int:
        """
        Рассчитывает общую стоимость всех товаров в корзине

        Args:
            user_id: ID пользователя

        Returns:
            Общая стоимость корзины
        """
        total_cost = await self.cart_repository.get_total_cost(user_id=user_id)
        return total_cost

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
        # Получаем информацию о продукте из product-service
        product = await get_product(product_id)
        product_price = product["price"]

        # Проверяем, есть ли уже этот товар в корзине
        existing_item = await self.cart_repository.get_cart_item_by_id(
            user_id=user_id,
            product_id=product_id
        )

        async with UnitOfWork(self.db):
            if existing_item:
                # Обновляем количество
                await self.cart_repository.update_cart_item(
                    user_id=user_id,
                    product_id=product_id,
                    quantity_add=quantity,
                    cost_add=product_price * quantity
                )
            else:
                # Добавляем новый товар
                await self.cart_repository.add_cart_item(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    total_cost=product_price * quantity
                )

    async def remove_cart_item(self, user_id: int, product_id: int) -> None:
        """
        Удаляет товар из корзины

        Args:
            user_id: ID пользователя
            product_id: ID товара для удаления
        """
        async with UnitOfWork(self.db):
            await self.cart_repository.remove_cart_item(
                user_id=user_id,
                product_id=product_id,
            )

    async def get_cart_items_with_products(self, user_id: int) -> list[SCartItemWithProduct]:
        """
        Получает товары корзины с подробной информацией о товарах.

        Args:
            user_id: ID пользователя

        Returns:
            Список товаров с детальной информацией
        """
        cart_items = await self.cart_repository.get_cart_items(user_id=user_id)
        
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
            except Exception:
                # Если продукт не найден, пропускаем его
                continue
        
        return result

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
        if quantity < 1:
            raise CannotHaveLessThan1Product

        existing_item = await self.cart_repository.get_cart_item_by_id(
            user_id=user_id,
            product_id=product_id
        )
        
        if not existing_item:
            raise NeedToHaveAProductToIncreaseItsQuantity

        # Получаем цену продукта из product-service
        product = await get_product(product_id)
        product_price = product["price"]

        async with UnitOfWork(self.db):
            total_cost = await self.cart_repository.update_quantity(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                price=product_price
            )
        return total_cost

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

