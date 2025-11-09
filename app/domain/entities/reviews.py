from dataclasses import dataclass
from typing import Optional


@dataclass
class ReviewItem:
    """Domain entity для отзывов"""
    user_id: int
    product_id: int
    feedback: str
    rating: int
    review_id: int | None = None  # None при создании, int после сохранения в БД
