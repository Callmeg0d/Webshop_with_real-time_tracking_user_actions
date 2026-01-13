from enum import Enum
from typing import Final


class HttpTimeout(float, Enum):
    """Таймауты для HTTP клиентов."""
    DEFAULT = 5.0
    GATEWAY = 10.0


class AnonymousUser:
    """Константы для анонимных пользователей."""
    EMAIL: Final[str] = "Анонимный пользователь"
    NAME: Final[None] = None


class HttpHeaders(str, Enum):
    """HTTP заголовки."""
    X_USER_ID = "X-User-Id"

