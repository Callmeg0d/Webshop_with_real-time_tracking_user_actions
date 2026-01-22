from typing import Optional
from dataclasses import dataclass

from shared.constants import DEFAULT_TEST_USER_ID

# Список ID продуктов, которые существуют в тестовой БД
EXISTING_PRODUCT_IDS = [
    4,
    14,
    44,
]


def get_existing_product_ids() -> list[int]:
    """Возвращает список ID существующих продуктов для тестов"""
    return EXISTING_PRODUCT_IDS.copy()


def get_existing_product_id() -> int:
    """Возвращает один существующий ID продукта для тестов"""
    return EXISTING_PRODUCT_IDS[0]


def get_nonexistent_product_id() -> int:
    """Возвращает несуществующий ID продукта для тестов"""
    return 99999


@dataclass
class ReviewTestData:
    """Фабрика для создания тестовых данных отзывов"""
    rating: int = 5
    feedback: str = "Отличный товар"
    user_id: int = DEFAULT_TEST_USER_ID
    product_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "rating": self.rating,
            "feedback": self.feedback
        }
    
    @classmethod
    def create_valid(cls, product_id: Optional[int] = None) -> "ReviewTestData":
        """Создает валидные данные для отзыва"""
        return cls(
            rating=5,
            feedback="Отличный товар",
            product_id=product_id or get_existing_product_id()
        )
    
    @classmethod
    def create_with_rating(cls, rating: int, product_id: Optional[int] = None) -> "ReviewTestData":
        """Создает данные с указанным рейтингом"""
        return cls(
            rating=rating,
            feedback="Тестовый отзыв",
            product_id=product_id or get_existing_product_id()
        )
    
    @classmethod
    def create_with_feedback(cls, feedback: str, product_id: Optional[int] = None) -> "ReviewTestData":
        """Создает данные с указанным отзывом"""
        return cls(
            rating=4,
            feedback=feedback,
            product_id=product_id or get_existing_product_id()
        )
