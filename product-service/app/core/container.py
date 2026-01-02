from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.products_repository import ProductsRepository
from app.repositories.categories_repository import CategoriesRepository
from app.services.product_service import ProductService
from app.services.category_service import CategoryService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    products_repository = providers.Factory(
        ProductsRepository,
        db=db
    )

    categories_repository = providers.Factory(
        CategoriesRepository,
        db=db
    )

    product_service = providers.Factory(
        ProductService,
        products_repository=products_repository,
        db=db
    )

    category_service = providers.Factory(
        CategoryService,
        category_repository=categories_repository,
        db=db
    )

