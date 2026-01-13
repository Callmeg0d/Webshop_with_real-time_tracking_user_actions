import httpx
from app.config import settings
from shared.constants import HttpTimeout


async def get_reviews(product_id: int) -> list[dict]:
    """Получает отзывы по продукту через review-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.REVIEW_SERVICE_URL}/reviews/{product_id}",
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()
        return response.json()

