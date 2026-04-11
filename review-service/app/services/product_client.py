import httpx
from fastapi import HTTPException, status

from app.config import settings
from shared import get_logger
from shared.constants import HttpTimeout

logger = get_logger(__name__)


async def ensure_product_exists(product_id: int) -> int:
    """
    Проверяет, что товар существует в product-service

    Args:
        product_id: ID товара

    Returns:
        product_id при успехе

    Raises:
        HTTPException: 404 если товар не найден; 502/503 при ошибке сервиса
    """
    url = f"{settings.PRODUCT_SERVICE_URL.rstrip('/')}/products/{product_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=HttpTimeout.DEFAULT.value)
    except httpx.RequestError as e:
        logger.error(f"Product service unreachable when checking product {product_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис каталога временно недоступен",
        ) from e

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товара с таким id не существует",
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.warning(
            f"Product service error for product {product_id}: {e.response.status_code}",
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка при проверке товара в каталоге",
        ) from e

    return product_id
