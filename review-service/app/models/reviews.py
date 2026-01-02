from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Reviews(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    product_id: Mapped[int] = mapped_column()
    feedback: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column(nullable=False)

