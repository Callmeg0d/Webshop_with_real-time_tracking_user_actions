from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShoppingCarts(Base):
    __tablename__ = "shopping_carts"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    product_id: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    total_cost: Mapped[int] = mapped_column()

