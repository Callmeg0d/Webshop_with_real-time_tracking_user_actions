import httpx

from app.config import settings
from shared.constants import HttpTimeout
from shared import get_logger


logger = get_logger(__name__)


def build_query_from_product(product: dict) -> str:
    """Формирует текстовый запрос для recommendations-service на основе данных товара"""
    name = str(product.get("name") or "").strip()
    description = str(product.get("description") or "").strip()
    category_name = str(product.get("category_name") or "").strip()
    features = product.get("features") or {}

    features_text = " ".join(f"{k} {v}" for k, v in features.items()) if isinstance(features, dict) else ""
    if len(description) > 400:
        description = description[:400] + "…"

    parts: list[str] = []
    if name:
        parts.append(f"Похожие товары на: {name}")
    if category_name:
        parts.append(f"категория: {category_name}")
    if description:
        parts.append(description)
    if features_text:
        parts.append(features_text)

    query = " ".join(parts).strip()
    return query or f"Похожие товары на продукт с id={product.get('product_id')}"


def build_query_from_products(products: list[dict]) -> str:
    """Склеивает запросы по нескольким товарам"""
    parts: list[str] = []
    for p in products:
        name = str(p.get("name") or "").strip()
        desc = str(p.get("description") or "").strip()
        if len(desc) > 400:
            desc = desc[:400] + "…"
        if name:
            parts.append(f"Похожие на: {name}")
        if desc:
            parts.append(desc)
    return " ".join(parts).strip() or "товары"


async def get_recommendations_for_product(product: dict, limit: int = 4) -> list[dict]:
    """Запрашивает похожие товары в recommendations-service по данным текущего товара

    В случае ошибок отдаёт пустой список, чтобы не ломать страницу товара
    """
    query = build_query_from_product(product)
    product_id = product.get("product_id")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RECOMMENDATIONS_SERVICE_URL}/recommend",
                json={"query": query, "limit": limit + 1},
                timeout=HttpTimeout.RECOMMENDATIONS.value,
            )
            response.raise_for_status()
            items: list[dict] = response.json()
    except httpx.TimeoutException as e:
        logger.warning(
            "Timeout while requesting recommendations for product %s from %s: %s",
            product_id,
            settings.RECOMMENDATIONS_SERVICE_URL,
            e,
        )
        return []
    except httpx.RequestError as e:
        logger.warning(
            "Recommendations unavailable for product %s (%s): %s",
            product_id,
            settings.RECOMMENDATIONS_SERVICE_URL,
            e,
        )
        return []
    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error from recommendations-service for product %s: status=%s, response=%s",
            product_id,
            e.response.status_code,
            e.response.text[:200],
        )
        return []

    # Фильтруем сам товар из рекомендаций, если он попал в выдачу
    if product_id is not None:
        items = [item for item in items if item.get("product_id") != product_id]

    return items[:limit]


async def get_recommendations_for_session(
    products: list[dict],
    limit: int = 8,
    exclude_product_ids: set[int] | None = None,
) -> list[dict]:
    """Рекомендации по нескольким товарам сессии (корзина или просмотренные)
    Строит общий запрос из всех товаров, запрашивает похожие, исключает уже имеющиеся.
    """
    if not products:
        return []

    query = build_query_from_products(products)
    basis_titles = [
        (p.get("name") or "")[:100] for p in products
    ]
    logger.info(
        "Session recommendations: запрос по %s товарам сессии (названия): %s | длина текста запроса=%s",
        len(products),
        basis_titles,
        len(query),
    )
    exclude = exclude_product_ids or set()
    # Запрашиваем с запасом, чтобы после исключения осталось limit
    request_limit = min(limit + len(exclude) + 4, 50)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RECOMMENDATIONS_SERVICE_URL}/recommend",
                json={"query": query, "limit": request_limit},
                timeout=HttpTimeout.RECOMMENDATIONS.value,
            )
            response.raise_for_status()
            items: list[dict] = response.json()
    except httpx.TimeoutException as e:
        logger.warning(
            "Timeout while requesting session recommendations from %s: %s",
            settings.RECOMMENDATIONS_SERVICE_URL,
            e,
        )
        return []
    except httpx.RequestError as e:
        logger.warning(
            "Session recommendations unavailable (%s): %s",
            settings.RECOMMENDATIONS_SERVICE_URL,
            e,
        )
        return []
    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error from recommendations-service (session): status=%s, response=%s",
            e.response.status_code,
            (e.response.text or "")[:200],
        )
        return []

    items = [item for item in items if item.get("product_id") not in exclude]
    return items[:limit]

