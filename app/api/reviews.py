from fastapi import APIRouter, Depends

from app.dependencies import get_reviews_service, get_current_user
from app.models import Users
from app.services.review_service import ReviewService
from app.schemas.reviews import SReviewCreate

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"]
)


@router.get("/{product_id}")
async def get_reviews(
        product_id: int,
        review_service: ReviewService = Depends(get_reviews_service)
):
    return await review_service.get_reviews(product_id)


@router.post("/{product_id}")
async def create_review(
        product_id: int,
        review_data: SReviewCreate,
        user: Users = Depends(get_current_user),
        review_service: ReviewService = Depends(get_reviews_service)
):
    review = await review_service.create_review(
        user_id=user.id,
        product_id=product_id,
        rating=review_data.rating,
        feedback=review_data.feedback
    )
    return review

