from fastapi import APIRouter, Depends

from app.dependencies import get_reviews_service
from shared import get_user_id, get_logger
from app.services.review_service import ReviewService
from app.schemas.reviews import SReviewCreate, SReviewWithUser

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"]
)

logger = get_logger(__name__)


@router.get("/{product_id}", response_model=list[SReviewWithUser])
async def get_reviews(
        product_id: int,
        review_service: ReviewService = Depends(get_reviews_service)
) -> list[SReviewWithUser]:
    logger.info(f"GET /reviews/{product_id} request")
    try:
        reviews = await review_service.get_reviews(product_id)
        logger.info(f"Returned {len(reviews)} reviews for product {product_id}")
        return reviews
    except Exception as e:
        logger.error(f"Error fetching reviews by API for product {product_id}: {e}", exc_info=True)
        raise


@router.post("/{product_id}")
async def create_review(
        product_id: int,
        review_data: SReviewCreate,
        user_id: int = Depends(get_user_id),
        review_service: ReviewService = Depends(get_reviews_service)
):
    logger.info(f"POST /reviews/{product_id} request from user {user_id}, rating: {review_data.rating}")
    try:
        review = await review_service.create_review(
            user_id=user_id,
            product_id=product_id,
            rating=review_data.rating,
            feedback=review_data.feedback
        )
        logger.info(f"Review created by API for product {product_id} by user {user_id}")
        return review
    except Exception as e:
        logger.error(f"Error creating review by API for product {product_id} by user {user_id}: {e}", exc_info=True)
        raise

