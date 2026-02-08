from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.idempotency_key import IdempotencyKeyItem
from app.domain.mappers.idempotency_key import IdempotencyKeyMapper
from app.models.idempotency import IdempotencyKey


class IdempotencyKeyRepository:
    """Репозиторий для ключей идемпотентности саги."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapper = IdempotencyKeyMapper()

    async def exists(self, key_type: str, business_key: str) -> bool:
        """Проверяет наличие ключа."""
        result = await self.db.execute(
            select(IdempotencyKey.id).where(
                IdempotencyKey.key_type == key_type,
                IdempotencyKey.business_key == business_key,
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def add(self, key_type: str, business_key: str) -> IdempotencyKeyItem:
        """Добавляет ключ."""
        entity = IdempotencyKeyItem(key_type=key_type, business_key=business_key)
        orm_model = IdempotencyKey(**self.mapper.to_orm(entity))
        self.db.add(orm_model)
        await self.db.flush()
        return self.mapper.to_entity(orm_model)
