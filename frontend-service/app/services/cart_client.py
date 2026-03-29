import httpx
from app.config import settings
from shared.constants import HttpTimeout, HttpHeaders


async def get_cart(user_id: int) -> list[dict]:
    """Получает корзину через cart-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CART_SERVICE_URL}/cart/",
            headers={HttpHeaders.X_USER_ID.value: str(user_id)},
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()
        return response.json()


def headers(user_id: int) -> dict[str, str]:
    return {HttpHeaders.X_USER_ID.value: str(user_id)}


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> None:
    """Добавляет товар в корзину через cart-service."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.CART_SERVICE_URL}/cart/{product_id}",
            params={"quantity": quantity},
            headers=headers(user_id),
            timeout=HttpTimeout.DEFAULT.value,
        )
        response.raise_for_status()


async def update_quantity(user_id: int, product_id: int, quantity: int) -> dict:
    """Обновляет количество товара в корзине. Возвращает {total_cost, cart_total}."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.CART_SERVICE_URL}/cart/{product_id}",
            json={"quantity": quantity},
            headers=headers(user_id),
            timeout=HttpTimeout.DEFAULT.value,
        )
        response.raise_for_status()
        return response.json()


async def remove_from_cart(user_id: int, product_id: int) -> None:
    """Удаляет товар из корзины через cart-service."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.CART_SERVICE_URL}/cart/{product_id}",
            headers=headers(user_id),
            timeout=HttpTimeout.DEFAULT.value,
        )
        response.raise_for_status()

