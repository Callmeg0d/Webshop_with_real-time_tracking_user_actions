import httpx
from app.config import settings
from shared.constants import DEFAULT_HTTP_TIMEOUT, X_USER_ID_HEADER


async def get_cart(user_id: int) -> list[dict]:
    """Получает корзину через cart-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CART_SERVICE_URL}/cart/",
            headers={X_USER_ID_HEADER: str(user_id)},
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

