from fastapi import APIRouter
from shared import get_logger

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

