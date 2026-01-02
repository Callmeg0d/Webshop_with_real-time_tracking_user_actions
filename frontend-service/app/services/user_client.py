import httpx
from app.config import settings
from shared.constants import DEFAULT_HTTP_TIMEOUT


async def login_user(email: str, password: str) -> dict:
    """Логин пользователя через user-service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.USER_SERVICE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


async def register_user(email: str, password: str) -> dict:
    """Регистрация пользователя через user-service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.USER_SERVICE_URL}/auth/register",
            json={"email": email, "password": password},
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


async def get_current_user(cookies: dict) -> dict | None:
    """Получает текущего пользователя через user-service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/auth/me",
                cookies=cookies,
                timeout=DEFAULT_HTTP_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


async def refresh_token(cookies: dict) -> bool:
    """Обновляет токен через user-service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/auth/refresh",
                cookies=cookies,
                timeout=DEFAULT_HTTP_TIMEOUT
            )
            return response.status_code == 200
        except Exception:
            return False

