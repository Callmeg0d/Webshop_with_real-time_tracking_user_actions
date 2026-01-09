from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work_factory import UnitOfWorkFactory
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

    uow_factory = providers.Factory(
        UnitOfWorkFactory,
        session=db
    )

    product_service = providers.Factory(
        ProductService,
        products_repository=products_repository,
        uow_factory=uow_factory
    )

    category_service = providers.Factory(
        CategoryService,
        category_repository=categories_repository,
        uow_factory=uow_factory
    )

