import httpx
from app.config import settings
from shared import get_logger
from shared.constants import (
    DEFAULT_HTTP_TIMEOUT,
    ANONYMOUS_USER_EMAIL,
    ANONYMOUS_USER_NAME,
    X_USER_ID_HEADER,
)

logger = get_logger(__name__)


async def get_user_info(user_id: int) -> dict:
    """
    Получает информацию о пользователе из user-service.

    Args:
        user_id: ID пользователя

    Returns:
        Словарь с данными пользователя (email, name)

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    logger.debug(f"Fetching user info for user {user_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/users/me",
                headers={X_USER_ID_HEADER: str(user_id)},
                timeout=DEFAULT_HTTP_TIMEOUT
            )
            response.raise_for_status()
            user_info = response.json()
            logger.debug(f"User info retrieved successfully for user {user_id}")
            return user_info
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching user info for user {user_id}: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"Error fetching user info for user {user_id}: {e}", exc_info=True)
        raise


async def get_users_batch(user_ids: list[int]) -> dict[int, dict]:
    """
    Получает информацию о нескольких пользователях из user-service батчем.

    Args:
        user_ids: Список ID пользователей

    Returns:
        Словарь вида {user_id: {email, name}}

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    if not user_ids:
        logger.debug("Empty user_ids list, returning empty dict")
        return {}
    
    logger.debug(f"Fetching batch user info for {len(user_ids)} users")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/users/batch",
                json={"user_ids": user_ids},
                timeout=DEFAULT_HTTP_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            # Преобразуем ответ в нужный формат
            result = {}
            users = data.get("users", {})
            for user_id, user_info in users.items():
                result[int(user_id)] = {
                    "email": user_info.get("email", ANONYMOUS_USER_EMAIL),
                    "name": user_info.get("name")
                }
            
            # Для пользователей, которых не нашли, добавляем дефолтные значения
            for user_id in user_ids:
                if user_id not in result:
                    result[user_id] = {
                        "email": ANONYMOUS_USER_EMAIL,
                        "name": ANONYMOUS_USER_NAME
                    }
            
            logger.debug(f"Batch user info retrieved successfully for {len(result)} users")
            return result
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching batch user info: {e.response.status_code}, using anonymous for all")
        # В случае ошибки возвращаем дефолтные значения для всех
        return {
            user_id: {
                "email": ANONYMOUS_USER_EMAIL,
                "name": ANONYMOUS_USER_NAME
            }
            for user_id in user_ids
        }
    except Exception as e:
        logger.error(f"Error fetching batch user info: {e}, using anonymous for all", exc_info=True)
        # В случае ошибки возвращаем дефолтные значения для всех
        return {
            user_id: {
                "email": ANONYMOUS_USER_EMAIL,
                "name": ANONYMOUS_USER_NAME
            }
            for user_id in user_ids
        }

