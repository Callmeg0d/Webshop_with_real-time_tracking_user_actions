from fastapi import APIRouter, Body, Depends

from app.reviews.dao import ReviewsDAO
from app.reviews.schemas import SReviews
from app.users.dependencies import get_current_user
from app.models.users import Users

router = APIRouter(
    prefix="/reviews",
    tags=["Отзывы"]
)


@router.post("/")
async def leave_review(user: Users = Depends(get_current_user),
                       review: SReviews = Body(...)):
    await ReviewsDAO.add_review(
        user_id=user.id,
        product_id=review.product_id,
        rating=review.rating,
        feedback=review.feedback
    )
    return {
        "user_name": user.email,
        "rating": review.rating,
        "feedback": review.feedback
    }
