from typing import Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.reviews import ReviewItem
from app.domain.mappers.review import ReviewMapper
from app.models import Reviews, Users


class ReviewRepository:
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

    async def get_reviews_with_users(self, product_id: int) -> List[dict[str, Any]]:
        """
        Получает отзывы по товару вместе с email авторов.

        Объединяет доменные данные отзывов с информацией о пользователях.

        Args:
            product_id: Идентификатор товара.

        Returns:
            Список DTO со связкой `user_email`, `rating`, `feedback`.
        """
        result = await self.db.execute(
            select(Reviews, Users.email)
            .join(Users, Reviews.user_id == Users.id)
            .where(Reviews.product_id == product_id)
        )
        # Оставим прям тут, так как просто DTO для чтения
        reviews = []
        for review, user_email in result.fetchall():
            reviews.append({
                "user_email": user_email or "Анонимный пользователь",
                "rating": review.rating,
                "feedback": review.feedback
            })

        return reviews