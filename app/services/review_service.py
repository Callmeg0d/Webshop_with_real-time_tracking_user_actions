from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.reviews import ReviewItem
from app.domain.interfaces.reviews_repo import IReviewsRepository
from app.domain.interfaces.users_repo import IUsersRepository


class ReviewService:
    def __init__(
            self,
            reviews_repository: IReviewsRepository,
            users_repository: IUsersRepository,
            db: AsyncSession
    ):
        self.reviews_repository = reviews_repository
        self.users_repository=users_repository
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
            created_review = await self.reviews_repository.create_review(review)
        
        # Получаем данные пользователя
        user = await self.users_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        return {
            "user_email": user.email,
            "user_name": user.name,
            "rating": created_review.rating,
            "feedback": created_review.feedback
        }

    async def get_reviews(self, product_id: int) -> list[dict]:
        reviews = await self.reviews_repository.get_reviews_with_users(product_id)
        return reviews