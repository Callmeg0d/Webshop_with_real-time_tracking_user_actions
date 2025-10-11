from typing import List

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reviews, Users
from app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Reviews]):
    def __init__(self, db: AsyncSession):
        super().__init__(Reviews, db)

    async def create_review(self, user_id: int, product_id: int, rating: int, feedback: str) -> None:
        result = await self.db.execute(
            insert(Reviews).values(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                feedback=feedback,
            )
        )
        return result

    async def get_reviews_with_users(self, product_id: int) -> List[dict]:
        """Получает отзывы по товару вместе с email авторов"""
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