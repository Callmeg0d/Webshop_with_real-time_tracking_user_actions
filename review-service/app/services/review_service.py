from shared import get_logger

from app.domain.entities.reviews import ReviewItem
from app.domain.interfaces.reviews_repo import IReviewsRepository
from app.domain.interfaces.unit_of_work import IUnitOfWorkFactory
from app.schemas.reviews import SReviewWithUser
from app.services.user_client import get_user_info, get_users_batch
from shared.constants import ANONYMOUS_USER_EMAIL, ANONYMOUS_USER_NAME

logger = get_logger(__name__)


class ReviewService:
    def __init__(
            self,
            reviews_repository: IReviewsRepository,
            uow_factory: IUnitOfWorkFactory
    ):
        self.reviews_repository = reviews_repository
        self.uow_factory = uow_factory

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
        logger.info(f"Creating review for product {product_id} by user {user_id}, rating: {rating}")
        try:
            review = ReviewItem(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                feedback=feedback,
            )
            async with self.uow_factory.create():
                created_review = await self.reviews_repository.create_review(review)
            
            logger.debug(f"Review created successfully, review_id: {created_review.review_id if hasattr(created_review, 'review_id') else 'N/A'}")
            
            # Получаем данные пользователя из user-service
            try:
                user = await get_user_info(user_id)
                user_email = user.get("email", ANONYMOUS_USER_EMAIL)
                user_name = user.get("name")
                logger.debug(f"User info retrieved for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to get user info for user {user_id}: {e}, using anonymous")
                user_email = ANONYMOUS_USER_EMAIL
                user_name = ANONYMOUS_USER_NAME

            logger.info(f"Review created successfully for product {product_id} by user {user_id}")
            return SReviewWithUser(
                user_email=user_email,
                user_name=user_name,
                rating=created_review.rating,
                feedback=created_review.feedback
            )
        except Exception as e:
            logger.error(f"Error creating review for product {product_id} by user {user_id}: {e}", exc_info=True)
            raise

    async def get_reviews(self, product_id: int) -> list[SReviewWithUser]:
        """
        Получает все отзывы по товару с данными пользователей.

        Args:
            product_id: ID товара

        Returns:
            Список отзывов с данными пользователей
        """
        logger.debug(f"Fetching reviews for product {product_id}")
        try:
            reviews = await self.reviews_repository.get_reviews_by_product(product_id)
            logger.debug(f"Found {len(reviews)} reviews for product {product_id}")
            
            if not reviews:
                return []
            
            # Получаем данные пользователей батчем
            user_ids = [review.user_id for review in reviews]
            users_info = await get_users_batch(user_ids)
            logger.debug(f"Retrieved user info for {len(users_info)} users")
            
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
            
            logger.debug(f"Returning {len(result)} reviews for product {product_id}")
            return result
        except Exception as e:
            logger.error(f"Error fetching reviews for product {product_id}: {e}", exc_info=True)
            raise

