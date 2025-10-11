from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from app.models.orders import Orders


class OrdersRepository(BaseRepository[Orders]):
    def __init__(self, db: AsyncSession):
        super().__init__(Orders, db)

    async def create_order(self, order_data: dict) -> Orders:
        """Создаёт новый заказ"""
        order = Orders(**order_data)
        self.db.add(order)
        return order

    async def get_by_user_id(self, user_id: int) -> List[Orders]:
        """Получает все заказы пользователя"""
        result = await self.db.execute(
            select(Orders).where(Orders.user_id == user_id)
        )
        return result.scalars().all()