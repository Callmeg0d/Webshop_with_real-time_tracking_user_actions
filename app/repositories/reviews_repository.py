from typing import List

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reviews, Users
from app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Reviews]):
    """
    Репозиторий для работы с отзывами.

    Предоставляет методы для создания и получения отзывов о товарах.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория отзывов.

        Args:
            db: Асинхронная сессия базы данных
        """
        super().__init__(Reviews, db)

    async def create_review(self, user_id: int, product_id: int, rating: int, feedback: str) -> Reviews:
        """
        Создаёт новый отзыв о товаре.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            rating: Оценка товара
            feedback: Текст отзыва

        Returns:
            Созданный объект отзыва
        """
        review = Reviews(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback,
        )
        self.db.add(review)
        return review

    async def get_reviews_with_users(self, product_id: int) -> List[dict]:
        """
        Получает отзывы по товару вместе с email авторов.

        Объединяет данные отзывов с информацией о пользователях.

        Args:
            product_id: ID товара

        Returns:
            Список словарей с информацией об отзывах и авторах
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