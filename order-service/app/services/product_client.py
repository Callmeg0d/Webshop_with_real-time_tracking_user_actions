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


async def get_stock_by_ids(product_ids: list[int]) -> dict[int, int]:
    """
    Получает остатки товаров на складе по списку ID из product-service.

    Args:
        product_ids: Список ID товаров

    Returns:
        Словарь вида {product_id: количество}

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.PRODUCT_SERVICE_URL}/products/stock/batch",
            json=product_ids,
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


async def decrease_stock(product_id: int, quantity: int) -> None:
    """
    Уменьшает остаток товара на складе в product-service.

    Args:
        product_id: ID товара
        quantity: Количество для уменьшения

    Raises:
        httpx.HTTPStatusError: Если сервис недоступен
    """
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}/stock",
            json={"quantity": -quantity},
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()

