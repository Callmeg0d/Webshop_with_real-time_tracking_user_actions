import logging
import httpx

from app.database.qdrant_client import QdrantStore
from app.services.reindex_products_to_qdrant import reindex_products_to_qdrant
from config import settings

logger = logging.getLogger(__name__)

MAX_PER_PAGE = 50


async def fetch_all_products_from_product_service(
    base_url: str,
    timeout: float = 120.0,
) -> list[dict]:
    """GET /products/count и постранично GET /products/."""
    base = base_url.rstrip("/")
    async with httpx.AsyncClient(timeout=timeout) as client:
        #Узнаёт общее число товаров
        r = await client.get(f"{base}/products/count")
        r.raise_for_status()
        total = int(r.json().get("total", 0))
        if total == 0:
            logger.warning("product-service: total=0 товаров")
            return []
        #Считает число страниц
        pages = (total + MAX_PER_PAGE - 1) // MAX_PER_PAGE

        all_rows = []
        for page in range(1, pages + 1):
            r = await client.get(
                f"{base}/products/",
                params={"page": page, "per_page": MAX_PER_PAGE, "order": "DESC"},
            )
            r.raise_for_status()
            batch = r.json()
            #Склеивает батчи, пока не пришла пустая страница
            if not batch:
                break
            all_rows.extend(batch)
            logger.info(
                "product-service: страница %d/%d, получено %d (всего %d)",
                page,
                pages,
                len(batch),
                len(all_rows),
            )

        return all_rows


async def bootstrap_qdrant_from_product_service_if_empty(store: QdrantStore) -> None:
    """
    Если коллекция Qdrant пуста (или отсутствует), тянем товары из product-service и индексируем.
    """
    url = (settings.PRODUCT_SERVICE_URL or "").strip()

    #Считает точки в коллекции
    n = await store.count_points(settings.DB_COLLECTION_NAME)
    if n > 0:
        logger.info("Qdrant коллекция %s: уже %d точек - пропускаем", settings.DB_COLLECTION_NAME, n)
        return

    logger.info(
        "Qdrant пустой или коллекция новая - загрузка каталога из product-service: %s",
        url,
    )
    #Если точек нет - получает из сервиса товаров
    try:
        products = await fetch_all_products_from_product_service(url)
    except Exception as e:
        logger.exception(
            "Не удалось получить товары из product-service (%s): %s - рекомендации будут пустыми до ручной загрузки/Kafka.",
            url,
            e,
        )
        return

    if not products:
        logger.warning("product-service вернул 0 товаров - Qdrant остаётся пустым")
        return

    try:
        #Загружаем полученные товары
        loaded = await reindex_products_to_qdrant(products, store)
        logger.info("В Qdrant загружено %d товаров", loaded)
    except Exception:
        logger.exception("Ошибка reindex_qdrant при bootstrap из product-service")
