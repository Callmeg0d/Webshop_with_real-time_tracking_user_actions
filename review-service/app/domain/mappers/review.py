from app.domain.entities.reviews import ReviewItem
from app.models.reviews import Reviews


class ReviewMapper:
    @staticmethod
    def to_entity(orm: Reviews) -> ReviewItem:
        """Преобразует ORM модель в domain entity."""
        return ReviewItem(
            review_id=orm.review_id,
            user_id=orm.user_id,
            product_id=orm.product_id,
            feedback=orm.feedback,
            rating=orm.rating,
        )

    @staticmethod
    def to_orm(entity: ReviewItem) -> dict[str, str|int]:
        """Преобразует entity в данные для ORM."""
        return {
            "user_id": entity.user_id,
            "product_id": entity.product_id,
            "feedback": entity.feedback,
            "rating": entity.rating,
        }

