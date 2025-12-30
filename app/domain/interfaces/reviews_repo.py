from typing import Protocol

from app.domain.entities.reviews import ReviewItem
from app.schemas.reviews import SReviewWithUser


class IReviewsRepository(Protocol):
    async def create_review(self, review: ReviewItem) -> ReviewItem:
        ...
    async def get_reviews_with_users(self, product_id: int) -> list[SReviewWithUser]:
        ...

