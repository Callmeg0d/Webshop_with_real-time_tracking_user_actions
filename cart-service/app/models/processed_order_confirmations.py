from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProcessedOrderConfirmation(Base):
    """Факт обработки события order_confirmed (идемпотентность при повторах из Kafka)"""

    __tablename__ = "processed_order_confirmations"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    processed_at: Mapped[datetime] = mapped_column(server_default=func.now())
