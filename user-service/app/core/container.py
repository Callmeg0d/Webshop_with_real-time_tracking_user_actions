from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work_factory import UnitOfWorkFactory
from app.repositories.users_repository import UsersRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    users_repository = providers.Factory(
        UsersRepository,
        db=db
    )

    uow_factory = providers.Factory(
        UnitOfWorkFactory,
        session=db
    )

    authentication_service = providers.Factory(
        AuthService,
        user_repository=users_repository,
        uow_factory=uow_factory,
        db=db
    )

    user_service = providers.Factory(
        UserService,
        user_repository=users_repository,
        uow_factory=uow_factory
    )