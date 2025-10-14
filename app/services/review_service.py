from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ReviewRepository


class ReviewService:
    def __init__(
            self,
            review_repository: ReviewRepository,
            db: AsyncSession
    ):
        self._review_repository = review_repository
        self.db = db

    async def create_review(
            self,
            user_id: int,
            product_id: int,
            rating: int,
            feedback: str
    ) -> None:
        await self._review_repository.create_review(user_id, product_id, rating, feedback)
        await self.db.commit()

    async def get_reviews(self, product_id: int) -> List[dict]:
        reviews = await self._review_repository.get_reviews_with_users(product_id)
        return reviews