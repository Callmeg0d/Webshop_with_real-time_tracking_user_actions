from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.reviews import ReviewItem
from app.domain.interfaces.reviews_repo import IReviewsRepository
from app.schemas.reviews import SReviewWithUser
from app.services.user_client import get_user_info, get_users_batch
from shared.constants import ANONYMOUS_USER_EMAIL, ANONYMOUS_USER_NAME


class ReviewService:
    def __init__(
            self,
            reviews_repository: IReviewsRepository,
            db: AsyncSession
    ):
        self.reviews_repository = reviews_repository
        self.db = db

    async def create_review(
            self,
            user_id: int,
            product_id: int,
            rating: int,
            feedback: str
    ) -> SReviewWithUser:
        """
        Создаёт новый отзыв о товаре.

        Args:
            user_id: ID пользователя
            product_id: ID товара
            rating: Рейтинг (1-5)
            feedback: Текст отзыва

        Returns:
            DTO отзыва с данными пользователя
        """
        review = ReviewItem(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback,
        )
        async with UnitOfWork(self.db):
            created_review = await self.reviews_repository.create_review(review)
        
        # Получаем данные пользователя из user-service
        try:
            user = await get_user_info(user_id)
            user_email = user.get("email", ANONYMOUS_USER_EMAIL)
            user_name = user.get("name")
        except Exception:
            user_email = ANONYMOUS_USER_EMAIL
            user_name = ANONYMOUS_USER_NAME

        return SReviewWithUser(
            user_email=user_email,
            user_name=user_name,
            rating=created_review.rating,
            feedback=created_review.feedback
        )

    async def get_reviews(self, product_id: int) -> list[SReviewWithUser]:
        """
        Получает все отзывы по товару с данными пользователей.

        Args:
            product_id: ID товара

        Returns:
            Список отзывов с данными пользователей
        """
        reviews = await self.reviews_repository.get_reviews_by_product(product_id)
        
        if not reviews:
            return []
        
        # Получаем данные пользователей батчем
        user_ids = [review.user_id for review in reviews]
        users_info = await get_users_batch(user_ids)
        
        result = []
        for review in reviews:
            user_info = users_info.get(review.user_id, {
                "email": ANONYMOUS_USER_EMAIL,
                "name": ANONYMOUS_USER_NAME
            })
            
            result.append(SReviewWithUser(
                user_email=user_info.get("email", ANONYMOUS_USER_EMAIL),
                user_name=user_info.get("name"),
                rating=review.rating,
                feedback=review.feedback
            ))
        
        return result

