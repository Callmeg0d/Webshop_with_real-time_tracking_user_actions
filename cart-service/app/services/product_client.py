import httpx
from app.config import settings
from shared.constants import DEFAULT_HTTP_TIMEOUT


async def get_product(product_id: int) -> dict:
    """
    Получает информацию о продукте из product-service.

    Args:
        product_id: ID продукта

    Returns:
        Словарь с данными продукта

    Raises:
        httpx.HTTPStatusError: Если продукт не найден или сервис недоступен
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

