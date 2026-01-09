from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import Container
from app.database import async_session_maker
from app.services.review_service import ReviewService
from shared import create_get_db

container = Container()

# Создаем get_db для этого сервиса
get_db = create_get_db(async_session_maker)


async def get_reviews_service(
        db: AsyncSession = Depends(get_db)
) -> ReviewService:
    """
    Получает сервис отзывов через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        ReviewService: Сервис для работы с отзывами
    """
    with container.db.override(db):
        return container.review_service()

