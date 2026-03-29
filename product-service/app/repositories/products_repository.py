from sqlalchemy import select, update, asc, desc, func, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.products import SortEnum, Pagination, SProductCreate, SProductUpdate
from app.domain.entities.product import ProductItem
from app.domain.mappers.product import ProductMapper
from app.models import Products


class ProductsRepository:
    """
    Репозиторий для работы с товарами.

    Работает с domain entities (ProductItem), используя маппер для преобразования
    между entities и ORM моделями.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Инициализация репозитория товаров.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = ProductMapper()

    async def get_stock_by_ids(self, product_ids: list[int]) -> dict[int, int]:
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

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        """
        Увеличивает количество конкретного товара (компенсация).

        Args:
            product_id: ID товара
            quantity: Количество для увеличения
        """
        await self.db.execute(
            update(Products)
            .where(Products.product_id == product_id)
            .values(product_quantity=Products.product_quantity + quantity)
        )

    async def get_quantity(self, product_id: int) -> int | None:
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

    async def get_product_by_id(self, product_id: int) -> ProductItem | None:
        """
        Возвращает доменную сущность товара по идентификатору.

        Args:
            product_id: Идентификатор товара.

        Returns:
            Доменная сущность товара если найден, иначе `None`.
        """
        result = await self.db.execute(
            select(Products).where(Products.product_id == product_id)
        )
        orm_product = result.scalar_one_or_none()
        return self.mapper.to_entity(orm_product) if orm_product else None

    async def get_products_by_ids(self, product_ids: list[int]) -> list[ProductItem]:
        """Возвращает список товаров по списку ID (порядок не гарантируется)."""
        if not product_ids:
            return []
        result = await self.db.execute(
            select(Products).where(Products.product_id.in_(product_ids))
        )
        orm_models = list(result.scalars().all())
        return [
            self.mapper.to_entity(orm_model)
            for orm_model in orm_models
            if orm_model is not None
        ]

    async def count_products(self) -> int:
        result = await self.db.execute(select(func.count(Products.product_id)))
        return int(result.scalar_one())

    async def get_all_products(self, pagination: Pagination) -> list[ProductItem]:
        """
        Возвращает список всех товаров в виде доменных сущностей.
        """
        order = desc if pagination.order == SortEnum.DESC else asc
        result = await self.db.execute(
            select(Products)
            .limit(pagination.per_page)
            .offset((pagination.page - 1) * pagination.per_page)
            .order_by(order(Products.product_id))
        )
        orm_models = list(result.scalars().all())
        return [
            self.mapper.to_entity(orm_model)
            for orm_model in orm_models
            if orm_model is not None
        ]

    async def add_product(self, product: SProductCreate) -> ProductItem:
        payload = product.model_dump(exclude_none=True)
        result = await self.db.execute(
            insert(Products).values(**payload).returning(Products)
        )
        row = result.scalar_one()
        return self.mapper.to_entity(row)

    async def update_product(self, product_id: int, data: SProductUpdate) -> ProductItem | None:
        payload = data.model_dump(exclude_none=True)
        if not payload:
            return await self.get_product_by_id(product_id)
        result = await self.db.execute(
            update(Products)
            .where(Products.product_id == product_id)
            .values(**payload)
            .returning(Products)
        )
        row = result.scalar_one_or_none()
        return self.mapper.to_entity(row) if row else None

    async def delete_product(self, product_id: int) -> ProductItem | None:
        result = await self.db.execute(
            delete(Products).where(Products.product_id == product_id).returning(Products)
        )
        row = result.scalar_one_or_none()
        return self.mapper.to_entity(row) if row else None

