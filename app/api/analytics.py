from fastapi import APIRouter, Request

from app.messaging.publisher import publish_tracker_event
from app.schemas.analytics import TrackerEvent

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/events")
async def receive_tracker_event(
    events: list[TrackerEvent],
) -> dict:
    for event in events:
        event_type = event.eventType

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

    return {"status": "ok"}