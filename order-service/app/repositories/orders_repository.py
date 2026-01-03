from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.domain.entities.orders import OrderItem
from app.domain.mappers.order import OrderMapper
from app.models.orders import Orders


class OrdersRepository:
    """Репозиторий для работы с заказами.

    Работает с domain entities (OrderItem), используя маппер для преобразования
    между entities и ORM моделями."""

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория заказов.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = OrderMapper()

    async def create_order(self, order: OrderItem) -> OrderItem:
        """
        Создаёт новый заказ.

        Args:
            order: Доменная сущность заказа, подготовленная слоем сервисов.

        Returns:
            Доменная сущность заказа с присвоенным идентификатором.
        """
        orm_data = self.mapper.to_orm(order)
        orm_model = Orders(**orm_data)
        self.db.add(orm_model)
        await self.db.flush()

        return self.mapper.to_entity(orm_model)

    async def get_by_user_id(self, user_id: int) -> list[OrderItem]:
        """
        Получает все заказы пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Список доменных сущностей заказов пользователя.
        """
        result = await self.db.execute(
            select(Orders).where(Orders.user_id == user_id)
        )
        orm_models = list(result.scalars().all())
        
        return [
            self.mapper.to_entity(orm_model)
            for orm_model in orm_models
            if orm_model is not None
        ]

    async def update_order_status(self, order_id: int, status: str) -> None:
        """
        Обновляет статус заказа.

        Args:
            order_id: ID заказа
            status: Новый статус
        """
        await self.db.execute(
            update(Orders)
            .where(Orders.order_id == order_id)
            .values(status=status)
        )

    async def get_order_by_id(self, order_id: int) -> OrderItem | None:
        """
        Получает заказ по ID.

        Args:
            order_id: ID заказа

        Returns:
            Доменная сущность заказа или None
        """
        result = await self.db.execute(
            select(Orders).where(Orders.order_id == order_id)
        )
        orm_model = result.scalar_one_or_none()
        return self.mapper.to_entity(orm_model) if orm_model else None

