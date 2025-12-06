from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.reviews import ReviewItem
from app.repositories import ReviewRepository, UsersRepository


class ReviewService:
    def __init__(
            self,
            review_repository: ReviewRepository,
            users_repository: UsersRepository,
            db: AsyncSession
    ):
        self._review_repository = review_repository
        self._users_repository = users_repository
        self.db = db

    async def create_review(
            self,
            user_id: int,
            product_id: int,
            rating: int,
            feedback: str
    ) -> dict:
        review = ReviewItem(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback,
        )
        async with UnitOfWork(self.db):
            created_review = await self._review_repository.create_review(review)
        
        # Получаем данные пользователя
        user = await self._users_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        return {
            "user_email": user.email,
            "user_name": user.name,
            "rating": created_review.rating,
            "feedback": created_review.feedback
        }

    async def get_reviews(self, product_id: int) -> List[dict]:
        reviews = await self._review_repository.get_reviews_with_users(product_id)
        return reviews