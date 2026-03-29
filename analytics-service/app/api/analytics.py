from fastapi import APIRouter, Query
from shared import get_logger

from app.analytics.clickhouse_client import get_clickhouse_client
from app.messaging.publisher import publish_tracker_event
from app.schemas.analytics import TrackerEvent

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger(__name__)


@router.post("/events")
async def receive_tracker_event(
    events: list[TrackerEvent],
) -> dict:
    """
    Принимает события аналитики от фронтенда и публикует их в Kafka.
    
    Args:
        events: Список событий для обработки
        
    Returns:
        Статус обработки
    """
    logger.info(f"POST /analytics/events request, received {len(events)} events")
    try:
        for event in events:
            event_type = event.eventType
            logger.debug(f"Processing event type: {event_type}")

            if event_type == "page_view":
                await publish_tracker_event(event.model_dump(), "page_views_topic")
            elif event_type == "click":
                await publish_tracker_event(event.model_dump(), "clicks_topic")
            elif event_type == "scroll":
                await publish_tracker_event(event.model_dump(), "scrolls_topic")
            elif event_type.startswith("custom_"):
                await publish_tracker_event(event.model_dump(), "custom_events_topic")
            else:
                await publish_tracker_event(event.model_dump(), "other_events_topic")

        logger.info(f"Successfully published {len(events)} events to Kafka")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing analytics events: {e}", exc_info=True)
        raise


@router.get("/viewed-products")
async def get_viewed_products_in_session(
    session_id: str = Query(..., description="ID сессии пользователя (tracker_session_id)"),
) -> dict:
    """
    Возвращает список product_id товаров, просмотренных в данной сессии (по событиям page_view в ClickHouse)
    Используется для рекомендаций «Вам может понравиться» на странице корзины
    """
    if not session_id or not session_id.strip():
        return {"product_ids": []}
    escaped = session_id.strip().replace("'", "''")
    try:
        ch = await get_clickhouse_client()
        sql = f"""
            SELECT product_id
            FROM (
                SELECT
                    toInt64OrZero(replaceRegexpOne(pathname, '^/product/([0-9]+).*', '\\1')) AS product_id,
                    max(event_time) AS last_seen
                FROM analytics.events
                WHERE session_id = '{escaped}'
                  AND pathname LIKE '/product/%'
                GROUP BY product_id
                HAVING product_id > 0
                ORDER BY last_seen DESC
                LIMIT 30
            )
        """
        rows = await ch.fetch(sql)
        product_ids = [int(row[0]) for row in rows if row and row[0]]
        return {"product_ids": product_ids}
    except Exception as e:
        logger.warning("Failed to get viewed products from ClickHouse: %s", e)
        return {"product_ids": []}

