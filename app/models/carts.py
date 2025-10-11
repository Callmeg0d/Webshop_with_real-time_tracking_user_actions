from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.products import Products
    from app.models.users import Users


class ShoppingCarts(Base):
    __tablename__ = "shopping_carts"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    quantity: Mapped[int] = mapped_column()
    total_cost: Mapped[int] = mapped_column()

    user: Mapped["Users"] = relationship("Users", back_populates="shopping_carts")
    product: Mapped["Products"] = relationship("Products", back_populates="shopping_carts")
