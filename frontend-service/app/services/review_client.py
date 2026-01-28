import httpx
from app.config import settings
from shared.constants import HttpTimeout
from shared import get_logger

logger = get_logger(__name__)


async def get_reviews(product_id: int) -> list[dict]:
    """Получает отзывы по продукту через review-service.

    В DEV, если review-service недоступен/таймаутится, не роняем страницу,
    а просто возвращаем пустой список.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.REVIEW_SERVICE_URL}/reviews/{product_id}",
                timeout=HttpTimeout.DEFAULT.value,
            )
            response.raise_for_status()
            reviews = response.json()
            logger.debug(f"Получено {len(reviews)} отзывов для продукта {product_id}")
            return reviews
    except httpx.TimeoutException as e:
        logger.warning(
            f"Таймаут при получении отзывов для продукта {product_id} "
            f"из {settings.REVIEW_SERVICE_URL}: {e}"
        )
        return []
    except httpx.RequestError as e:
        logger.error(
            f"Ошибка подключения к review-service для продукта {product_id}: {e}",
            exc_info=True
        )
        return []
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP ошибка при получении отзывов для продукта {product_id}: "
            f"status={e.response.status_code}, response={e.response.text[:200]}"
        )
        return []

