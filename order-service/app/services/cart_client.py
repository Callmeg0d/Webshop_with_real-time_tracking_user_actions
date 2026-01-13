import httpx
from app.config import settings
from shared.constants import HttpTimeout, HttpHeaders


async def get_cart_items(user_id: int) -> list[dict]:
    """
    Получает товары из корзины пользователя из cart-service.

    Args:
        user_id: ID пользователя

    Returns:
        Список товаров в корзине

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CART_SERVICE_URL}/cart/",
            headers={HttpHeaders.X_USER_ID.value: str(user_id)},
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()
        return response.json()


async def get_cart_total(user_id: int) -> int:
    """
    Получает общую стоимость корзины из cart-service.

    Args:
        user_id: ID пользователя

    Returns:
        Общая стоимость корзины

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    # Можно получить из корзины или сделать отдельный endpoint
    # Пока считаем на основе товаров
    items = await get_cart_items(user_id)
    return sum(item.get("total_cost", 0) for item in items)


async def clear_cart(user_id: int) -> None:
    """
    Очищает корзину пользователя в cart-service.

    Args:
        user_id: ID пользователя

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.CART_SERVICE_URL}/cart/clear",
            headers={HttpHeaders.X_USER_ID.value: str(user_id)},
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()

