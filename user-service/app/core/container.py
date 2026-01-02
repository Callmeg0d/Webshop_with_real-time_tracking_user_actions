from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

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

    authentication_service = providers.Factory(
        AuthService,
        user_repository=users_repository,
        db=db
    )

    user_service = providers.Factory(
        UserService,
        user_repository=users_repository,
        db=db
    )

