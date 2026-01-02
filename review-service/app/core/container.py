from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.reviews_repository import ReviewsRepository
from app.services.review_service import ReviewService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    reviews_repository = providers.Factory(
        ReviewsRepository,
        db=db
    )

    review_service = providers.Factory(
        ReviewService,
        reviews_repository=reviews_repository,
        db=db
    )

