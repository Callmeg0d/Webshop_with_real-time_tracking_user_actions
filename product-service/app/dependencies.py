from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import Container
from app.database import async_session_maker
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from shared import create_get_db


container = Container()

# Создаем get_db для этого сервиса
get_db = create_get_db(async_session_maker)


async def get_products_service(
        db: AsyncSession = Depends(get_db)
) -> ProductService:
    """
    Получает сервис товаров через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        ProductService: Сервис для работы с товарами
    """
    with container.db.override(db):
        return container.product_service()


async def get_categories_service(
        db: AsyncSession = Depends(get_db)
) -> CategoryService:
    """
    Получает сервис категорий через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        CategoryService: Сервис для работы с категориями
    """
    with container.db.override(db):
        return container.category_service()

