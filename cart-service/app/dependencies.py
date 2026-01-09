from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import Container
from app.database import async_session_maker
from app.services.cart_service import CartService
from shared import create_get_db

container = Container()

# Создаем get_db для этого сервиса
get_db = create_get_db(async_session_maker)


async def get_carts_service(
        db: AsyncSession = Depends(get_db)
) -> CartService:
    """
    Получает сервис корзины через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        CartService: Сервис для работы с корзиной
    """
    with container.db.override(db):
        return container.cart_service()

