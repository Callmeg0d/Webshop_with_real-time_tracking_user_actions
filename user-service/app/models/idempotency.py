from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IdempotencyKey(Base):
    """Ключи идемпотентности для саги (обработка заказа, компенсации)."""

    __tablename__ = "idempotency_keys"
    __table_args__ = (UniqueConstraint("key_type", "business_key", name="uq_idempotency_key_type_business"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key_type: Mapped[str] = mapped_column(String(64), nullable=False)
    business_key: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
