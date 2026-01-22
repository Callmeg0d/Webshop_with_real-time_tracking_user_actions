import pytest
from shared.constants import HttpHeaders, DEFAULT_TEST_USER_ID


@pytest.fixture
def auth_headers_with_user_id():
    """Фабрика для создания заголовков авторизации с указанным user_id"""
    def _create_headers(user_id: int) -> dict:
        return {
            HttpHeaders.X_USER_ID.value: str(user_id)
        }
    return _create_headers


@pytest.fixture
def auth_headers(auth_headers_with_user_id):
    """Создает заголовки авторизации с дефолтным user_id"""
    return auth_headers_with_user_id(DEFAULT_TEST_USER_ID)
