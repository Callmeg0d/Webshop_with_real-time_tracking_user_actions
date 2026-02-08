from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderSagaReservation(Base):
    """Состояние резерваций саги по заказу."""

    __tablename__ = "order_saga_reservations"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    stock_done: Mapped[bool] = mapped_column(Boolean, default=False)
    balance_done: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
