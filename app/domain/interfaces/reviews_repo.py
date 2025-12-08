from typing import Protocol, Any, List

from app.domain.entities.reviews import ReviewItem


class IReviewsRepository(Protocol):
    async def create_review(self, review: ReviewItem) -> ReviewItem:
        ...

    async def get_reviews_with_users(self, product_id: int) -> List[dict[str, Any]]:
        ...

