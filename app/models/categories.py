from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class Categories(Base):
    __tablename__ = "categories"

    category_name: Mapped[str] = mapped_column(primary_key=True)
