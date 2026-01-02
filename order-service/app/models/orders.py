from datetime import date
from typing import Dict, List

from sqlalchemy import JSON, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Orders(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    created_at: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column()
    delivery_address: Mapped[str] = mapped_column()
    order_items: Mapped[List[Dict[str, str | int]]] = mapped_column(JSON)
    total_cost: Mapped[int] = mapped_column()

