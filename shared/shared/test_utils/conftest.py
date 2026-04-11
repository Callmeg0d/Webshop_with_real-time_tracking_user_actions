from collections.abc import Callable

import pytest

from shared.constants import DEFAULT_TEST_USER_ID, HttpHeaders


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Заголовки с X-User-Id по умолчанию (DEFAULT_TEST_USER_ID)."""
    return {HttpHeaders.X_USER_ID.value: str(DEFAULT_TEST_USER_ID)}


@pytest.fixture
def auth_headers_with_user_id() -> Callable[[int], dict[str, str]]:
    """Фабрика заголовков с заданным user_id."""

    def _make(user_id: int) -> dict[str, str]:
        return {HttpHeaders.X_USER_ID.value: str(user_id)}

    return _make
