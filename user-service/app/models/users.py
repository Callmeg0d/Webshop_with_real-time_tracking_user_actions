from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    delivery_address: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    balance: Mapped[int] = mapped_column(default=0, server_default="0")

    def __str__(self):
        return f"User {self.email}"
