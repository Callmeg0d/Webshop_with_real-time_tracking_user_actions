from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Products
from app.repositories.base_repository import BaseRepository


class ProductsRepository(BaseRepository[Products]):
    """
    Репозиторий для работы с товарами.

    Предоставляет методы для управления товарами, включая получение информации,
    обновление количества на складе и получение цен.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория товаров.

        Args:
            db: Асинхронная сессия базы данных
        """
        super().__init__(Products, db)

    async def get_stock_by_ids(self, product_ids: List[int]) -> dict:
        """
        Получает количество товаров на складе по списку ID.

        Args:
            product_ids: Список ID товаров

        Returns:
            Словарь вида {product_id: количество}
        """
        result = await self.db.execute(
            select(Products.product_id, Products.product_quantity)
            .where(Products.product_id.in_(product_ids))
        )
        return {
            item["product_id"]: item["product_quantity"]
            for item in result.mappings().all()
        }

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        """
        Уменьшает количество конкретного товара.

        Args:
            product_id: ID товара
            quantity: Количество для уменьшения
        """
        await self.db.execute(
            update(Products)
            .where(Products.product_id == product_id)
            .values(product_quantity=Products.product_quantity - quantity)
        )

    async def get_quantity(self, product_id: int) -> Optional[int]:
        """
        Получает количество конкретного товара.

        Args:
            product_id: ID товара

        Returns:
            Количество товара если найден, иначе None
        """
        result = await self.db.execute(
            select(Products.product_quantity)
            .where(Products.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_product_by_id(self, product_id: int) -> Optional[Products]:
        """
        Получает полную информацию о товаре по его ID.

        Args:
            product_id: ID товара

        Returns:
            Словарь с информацией о товаре если найден, иначе None
        """
        result = await self.db.execute(
            select(
                Products.product_id,
                Products.name,
                Products.description,
                Products.price,
                Products.product_quantity,
                Products.image,
                Products.features,
                Products.category_name,
            ).where(Products.product_id == product_id)
        )
        return result.mappings().first()

    async def get_price(self, product_id: int) -> Optional[int]:
        """
        Получает цену товара.

        Args:
            product_id: ID товара

        Returns:
            Цена товара если найден, иначе None
        """
        result = await self.db.execute(
            select(Products.price)
            .where(Products.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_price_and_stock(self, product_id: int) -> Optional[dict]:
        """
        Получает цену и количество товара.

        Args:
            product_id: ID товара

        Returns:
            Словарь с ключами price и stock если найден, иначе None
        """
        result = await self.db.execute(
            select(Products.price, Products.product_quantity)
            .where(Products.product_id == product_id)
        )
        row = result.first()
        if row:
            return {"price": row.price, "stock": row.product_quantity}
        return None