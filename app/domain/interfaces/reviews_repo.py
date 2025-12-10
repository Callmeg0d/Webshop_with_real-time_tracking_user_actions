from typing import Protocol, Any

from app.domain.entities.reviews import ReviewItem


class IReviewsRepository(Protocol):
    async def create_review(self, review: ReviewItem) -> ReviewItem:
        ...
    # todo: Убрать Any
    async def get_reviews_with_users(self, product_id: int) -> list[dict[str, Any]]:
        ...

