from typing import Any, Dict, List

from fastapi import APIRouter, Request

from app.messaging.publisher import publish_tracker_event

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/events")
async def receive_tracker_event(
    events: List[Dict[str, Any]],
    request: Request,
) -> dict:
    for event in events:
        event_type = event.get("eventType", "")

        if event_type == "page_view":
            await publish_tracker_event(event, "page_views_topic")
        elif event_type == "click":
            await publish_tracker_event(event, "clicks_topic")
        elif event_type == "scroll":
            await publish_tracker_event(event, "scrolls_topic")
        elif event_type.startswith("custom_"):
            await publish_tracker_event(event, "custom_events_topic")
        else:
            await publish_tracker_event(event, "other_events_topic")

    return {"status": "ok"}