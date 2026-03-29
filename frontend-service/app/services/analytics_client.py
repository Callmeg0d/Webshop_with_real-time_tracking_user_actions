import httpx
from app.config import settings
from shared import get_logger
from shared.constants import HttpTimeout

logger = get_logger(__name__)


async def get_viewed_product_ids(session_id: str) -> list[int]:
    """
    Возвращает список product_id товаров, просмотренных в данной сессии (по ClickHouse).
    Пустой session_id возвращает [].
    """
    if not session_id or not session_id.strip():
        return []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ANALYTICS_SERVICE_URL}/analytics/viewed-products",
                params={"session_id": session_id.strip()},
                timeout=HttpTimeout.DEFAULT.value,
            )
            response.raise_for_status()
            data = response.json()
            return list(data.get("product_ids") or [])
    except httpx.TimeoutException as e:
        logger.warning("Timeout requesting viewed products from analytics: %s", e)
        return []
    except httpx.RequestError as e:
        logger.warning("Analytics service unavailable (viewed-products): %s", e)
        return []
    except Exception as e:
        logger.warning("Failed to get viewed product ids: %s", e)
        return []
