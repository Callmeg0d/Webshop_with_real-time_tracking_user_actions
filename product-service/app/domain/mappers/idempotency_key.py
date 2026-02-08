from app.domain.entities.idempotency_key import IdempotencyKeyItem
from app.models.idempotency import IdempotencyKey


class IdempotencyKeyMapper:
    @staticmethod
    def to_entity(orm_model: IdempotencyKey) -> IdempotencyKeyItem:
        """Преобразует ORM модель в domain entity."""
        return IdempotencyKeyItem(
            id=orm_model.id,
            key_type=orm_model.key_type,
            business_key=orm_model.business_key,
            created_at=orm_model.created_at,
        )

    @staticmethod
    def to_orm(entity: IdempotencyKeyItem) -> dict:
        """Преобразует entity в данные для ORM."""
        return {
            "key_type": entity.key_type,
            "business_key": entity.business_key,
        }
