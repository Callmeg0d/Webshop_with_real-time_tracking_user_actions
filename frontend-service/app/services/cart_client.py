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

