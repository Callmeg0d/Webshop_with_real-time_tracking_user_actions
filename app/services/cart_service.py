from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.cart import CartItem
from app.repositories import CartsRepository


class CartService:
    def __init__(
            self,
            cart_repository: CartsRepository,
            db: AsyncSession
    ):
        """
        Сервис для управления корзиной покупок пользователя

        Args:
            cart_repository: Репозиторий для работы с корзиной в БД
            db: Асинхронная сессия базы данных
        """
        self.cart_repository = cart_repository
        self.db = db

    async def get_user_cart(self, user_id: int) -> List[dict]:
        """
        Общая идея: Получает все товары в корзине пользователя

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

    async def update_cart_item(
            self,
            user_id: int,
            product_id: int,
            quantity_add: int,
            cost_add: int
    ) -> None:
        """
        Обновляет количество и стоимость товара в корзине

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity_add: Количество для добавления
            cost_add: Стоимость для добавления
        """

        async with UnitOfWork(self.db):
            await self.cart_repository.update_cart_item(
                user_id=user_id,
                product_id=product_id,
                quantity_add=quantity_add,
                cost_add=cost_add
            )

    async def add_cart_item(self,
                            user_id: int,
                            product_id: int,
                            quantity: int,
                            total_cost: int
    ) -> None:
        """
        Добавляет новый товар в корзину

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity: Количество товара
            total_cost: Общая стоимость товара
        """
        async with UnitOfWork(self.db):
            await self.cart_repository.add_cart_item(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                total_cost=total_cost
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

    async def get_cart_items_with_products(self, user_id: int) -> List[dict]:
        """
        Получает товары корзины с подробной информацией о товарах

        Args:
            user_id: ID пользователя

        Returns:
            Список товаров с детальной информацией
        """
        cart_items = await self.cart_repository.get_cart_items_with_products(user_id=user_id)
        return cart_items

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
        async with UnitOfWork(self.db):
            total_cost = await self.cart_repository.update_quantity(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
            )
        return total_cost

    async def get_cart_item_by_id(self, user_id: int, product_id: int) -> Optional[CartItem]:
        """
        Находит конкретный товар в корзине пользователя по id

        Args:
            user_id: ID пользователя
            product_id: ID товара

        Returns:
            Найденный товар или None если не найден
        """
        return await self.cart_repository.get_cart_item_by_id(user_id=user_id, product_id=product_id)

