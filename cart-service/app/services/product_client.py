import httpx
from app.config import settings
from shared import get_logger
from shared.constants import DEFAULT_HTTP_TIMEOUT

logger = get_logger(__name__)


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
    logger.debug(f"Fetching product {product_id} from product-service")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
                timeout=DEFAULT_HTTP_TIMEOUT
            )
            response.raise_for_status()
            product = response.json()
            logger.debug(f"Product {product_id} retrieved successfully")
            return product
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching product {product_id}: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}", exc_info=True)
        raise

