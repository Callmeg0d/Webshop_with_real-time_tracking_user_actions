from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.carts_repository import CartsRepository
from app.services.cart_service import CartService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    carts_repository = providers.Factory(
        CartsRepository,
        db=db
    )

    cart_service = providers.Factory(
        CartService,
        carts_repository=carts_repository,
        db=db
    )

