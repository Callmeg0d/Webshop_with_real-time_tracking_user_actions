from typing import Protocol

from app.domain.entities.reviews import ReviewItem


class IReviewsRepository(Protocol):
    async def create_review(self, review: ReviewItem) -> ReviewItem:
        ...
    
    async def get_reviews_by_product(self, product_id: int) -> list[ReviewItem]:
        ...

