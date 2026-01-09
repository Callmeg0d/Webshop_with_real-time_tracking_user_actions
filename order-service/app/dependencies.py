from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import Container
from app.database import async_session_maker
from app.services.order_service import OrderService
from shared import create_get_db

container = Container()

# Создаем get_db для этого сервиса
get_db = create_get_db(async_session_maker)


async def get_orders_service(
        db: AsyncSession = Depends(get_db)
) -> OrderService:
    """
    Получает сервис заказов через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        OrderService: Сервис для работы с заказами
    """
    with container.db.override(db):
        return container.order_service()

