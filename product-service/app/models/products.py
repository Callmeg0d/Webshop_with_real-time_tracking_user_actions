from typing import Optional, Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Products(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    product_quantity: Mapped[int] = mapped_column()
    image: Mapped[Optional[str]] = mapped_column(nullable=True)
    features: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    category_id: Mapped[int] = mapped_column()

