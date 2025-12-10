from sqlalchemy import select, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ShoppingCarts, Products
from app.domain.entities.cart import CartItem
from app.domain.mappers.cart import CartMapper


class CartsRepository:
    """
    Репозиторий для работы с корзиной товаров.

    Работает с domain entities (CartItem), используя маппер для преобразования
    между entities и ORM моделями.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория корзины.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = CartMapper()

    async def clear_cart(self, user_id: int) -> None:
        """
        Очищает корзину пользователя.

        Args:
            user_id: ID пользователя
        """
        await self.db.execute(
            delete(ShoppingCarts).where(ShoppingCarts.user_id == user_id)
        )

    async def get_cart_items(self, user_id: int) -> list[dict]:
        """
        Получает товары из корзины пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Список словарей с информацией о товарах в корзине
        """
        result = await self.db.execute(
            select(
                ShoppingCarts.product_id,
                ShoppingCarts.quantity,
                ShoppingCarts.total_cost
            )
            .where(ShoppingCarts.user_id == user_id)
        )
        items = result.mappings().all()
        return [dict(item) for item in items]

    async def get_total_cost(self, user_id: int) -> int:
        """
        Получает общую стоимость товаров в корзине.

        Args:
            user_id: ID пользователя

        Returns:
            Общая стоимость корзины
        """
        result = await self.db.execute(
            select(func.sum(ShoppingCarts.total_cost))
            .where(ShoppingCarts.user_id == user_id)
        )
        return result.scalar() or 0

    async def update_cart_item(self, user_id: int, product_id: int,
                               quantity_add: int, cost_add: int) -> None:
        """
        Увеличивает количество и стоимость товара в корзине.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity_add: Количество для добавления
            cost_add: Стоимость для добавления
        """
        await self.db.execute(
            update(ShoppingCarts)
            .where(
                ShoppingCarts.user_id == user_id,
                ShoppingCarts.product_id == product_id
            )
            .values(
                quantity=ShoppingCarts.quantity + quantity_add,
                total_cost=ShoppingCarts.total_cost + cost_add
            )
        )

    async def add_cart_item(self, user_id: int, product_id: int,
                            quantity: int, total_cost: int) -> CartItem:
        """
        Добавляет новый товар в корзину.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity: Количество товара
            total_cost: Общая стоимость

        Returns:
            Созданная domain entity корзины
        """
        cart_entity = CartItem(
            cart_id=None,  # None при создании
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_cost=int(total_cost)
        )

        orm_data = self.mapper.to_orm(cart_entity)
        orm_model = ShoppingCarts(**orm_data)
        self.db.add(orm_model)
        await self.db.flush()  # Получаем cart_id из БД
        
        # Возвращаем entity с реальным ID
        return self.mapper.to_entity(orm_model)

    async def remove_cart_item(self, user_id: int, product_id: int) -> None:
        """
        Удаляет конкретный товар из корзины.

        Args:
            user_id: ID пользователя
            product_id: ID товара
        """
        await self.db.execute(
            delete(ShoppingCarts).where(
                ShoppingCarts.user_id == user_id,
                ShoppingCarts.product_id == product_id
            )
        )

    async def get_cart_items_with_products(self, user_id: int) -> list[dict]:
        """
        Получает товары из корзины с полной информацией о товарах.

        Объединяет данные корзины с информацией из таблицы продуктов.

        Args:
            user_id: ID пользователя

        Returns:
            Список словарей с полной информацией о товарах в корзине
        """
        result = await self.db.execute(
            select(
                ShoppingCarts.product_id,
                Products.name,
                Products.description,
                Products.price,
                ShoppingCarts.quantity,
                (Products.price * ShoppingCarts.quantity).label("total_cost"),
                Products.product_quantity,
            )
            .join(Products, ShoppingCarts.product_id == Products.product_id)
            .where(ShoppingCarts.user_id == user_id)
        )
        items = result.mappings().all()
        return [dict(item) for item in items]


    async def update_quantity(self, user_id: int, product_id: int, quantity: int) -> int:
        """
        Обновляет количество товара в корзине и пересчитывает стоимость.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            quantity: Новое количество товара

        Returns:
            Новая общая стоимость позиции
        """
        result = await self.db.execute(
            update(ShoppingCarts)
            .where(
                ShoppingCarts.user_id == user_id,
                ShoppingCarts.product_id == product_id
            )
            .values(
                quantity=quantity,
                total_cost=select(Products.price * quantity)
                .where(Products.product_id == product_id)
                .scalar_subquery()
            )
            .returning(ShoppingCarts.total_cost)
        )
        row = result.fetchone()
        return row[0] if row else 0

    async def get_cart_item_by_id(self, user_id: int, product_id: int) -> CartItem | None:
        """
        Получает конкретный товар из корзины пользователя.

        Args:
            user_id: ID пользователя
            product_id: ID товара

        Returns:
            Domain entity корзины если найдена, иначе None
        """
        result = await self.db.execute(
            select(ShoppingCarts).where(
                ShoppingCarts.user_id == user_id,
                ShoppingCarts.product_id == product_id
            )
        )
        orm_model = result.scalar_one_or_none()
        
        if not orm_model:
            return None
        
        return self.mapper.to_entity(orm_model)
