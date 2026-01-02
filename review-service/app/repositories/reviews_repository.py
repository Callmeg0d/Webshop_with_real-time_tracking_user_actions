from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.reviews import ReviewItem
from app.domain.mappers.review import ReviewMapper
from app.models.reviews import Reviews


class ReviewsRepository:
    """
    Репозиторий для работы с отзывами.

    Работает с domain entities (ReviewItem), используя маппер для преобразования
    между entities и ORM моделями.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория отзывов.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = ReviewMapper()

    async def create_review(self, review: ReviewItem) -> ReviewItem:
        """
        Создаёт новый отзыв о товаре.

        Args:
            review: Доменная сущность отзыва, подготовленная слоем сервисов.

        Returns:
            Доменная сущность отзыва с заполненным `review_id`.
        """
        orm_data = self.mapper.to_orm(review)
        orm_model = Reviews(**orm_data)
        self.db.add(orm_model)
        await self.db.flush()

        return self.mapper.to_entity(orm_model)

    async def get_reviews_by_product(self, product_id: int) -> list[ReviewItem]:
        """
        Получает все отзывы по товару.

        Args:
            product_id: Идентификатор товара.

        Returns:
            Список доменных сущностей отзывов.
        """
        result = await self.db.execute(
            select(Reviews).where(Reviews.product_id == product_id)
        )
        orm_models = list(result.scalars().all())
        
        return [
            self.mapper.to_entity(orm_model)
            for orm_model in orm_models
            if orm_model is not None
        ]

