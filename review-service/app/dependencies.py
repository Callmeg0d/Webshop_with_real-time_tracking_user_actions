from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import Container
from app.database import async_session_maker
from app.services.review_service import ReviewService
from shared import create_get_db

container = Container()

# Создаем get_db для этого сервиса
get_db = create_get_db(async_session_maker)


async def check_product_exists(product_id: int) -> int:
    """
    Проверяет существование продукта
    
    Args:
        product_id: ID продукта
        
    Returns:
        product_id если продукт существует
        
    Raises:
        HTTPException: 404 если продукт не найден
    """
    # TODO: В prod добавить вызов product-service
    # Пока всегда возвращаем успех
    return product_id


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

