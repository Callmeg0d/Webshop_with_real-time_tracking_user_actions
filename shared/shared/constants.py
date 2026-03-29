from enum import Enum
from typing import Final


class HttpTimeout(float, Enum):
    """Таймауты для HTTP клиентов."""
    DEFAULT = 5.0
    GATEWAY = 10.0
    RECOMMENDATIONS = 20.0


class AnonymousUser:
    """Константы для анонимных пользователей."""
    EMAIL: Final[str] = "Анонимный пользователь"
    NAME: Final[None] = None


class HttpHeaders(str, Enum):
    """HTTP заголовки."""
    X_USER_ID = "X-User-Id"


class SagaIdempotencyKey:
    """Типы ключей идемпотентности для саги."""
    ORDER_PROCESSING: Final[str] = "order_processing"
    COMPENSATION_BALANCE: Final[str] = "compensation_balance"
    COMPENSATION_STOCK: Final[str] = "compensation_stock"


class ReserveBalanceResult(str, Enum):
    """Результат резервации баланса в саге."""
    ALREADY_DONE = "already_done"
    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found"
    INSUFFICIENT_BALANCE = "insufficient_balance"


class ReserveStockResult(str, Enum):
    """Результат резервации остатков в саге."""
    ALREADY_DONE = "already_done"
    SUCCESS = "success"
    INSUFFICIENT_STOCK = "insufficient_stock"


# Тестовые константы
DEFAULT_TEST_USER_ID: Final[int] = 1

