from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryItem:
    """Domain entity для категории товаров."""
    id: int | None  # None при создании, int после сохранения в БД
    name: str
    description: Optional[str]
