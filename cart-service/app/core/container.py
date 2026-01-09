from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work_factory import UnitOfWorkFactory
from app.repositories.carts_repository import CartsRepository
from app.services.cart_service import CartService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    carts_repository = providers.Factory(
        CartsRepository,
        db=db
    )

    uow_factory = providers.Factory(
        UnitOfWorkFactory,
        session=db
    )

    cart_service = providers.Factory(
        CartService,
        carts_repository=carts_repository,
        uow_factory=uow_factory
    )

