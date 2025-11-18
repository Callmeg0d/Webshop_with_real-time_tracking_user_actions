import json
import smtplib
from datetime import datetime, timezone

from faststream.kafka import KafkaRouter
from pydantic import EmailStr

from app.analytics.clickhouse_client import get_clickhouse_client
from app.config import settings
from app.messaging.email_templates import (
    create_order_confirmation_template,
    create_registration_confirmation_template,
)

router = KafkaRouter()


@router.subscriber("registration_confirmation", group_id="email_service")
async def handle_registration_confirmation(email_to: EmailStr) -> None:
    msg_context = create_registration_confirmation_template(email_to)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)


@router.subscriber("order_confirmation", group_id="email_service")
async def handle_order_confirmation(order: dict, email_to: EmailStr) -> None:
    msg_context = create_order_confirmation_template(order, email_to)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)


@router.subscriber("clicks_topic", group_id="analytics")
async def handle_click_event(event: dict) -> None:
    ch = await get_clickhouse_client()

    ts_ms = event.get("timestamp")
    if ts_ms is None:
        event_time = datetime.now(timezone.utc)
    else:
        event_time = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

    element = event.get("element") or {}

    await ch.execute(
        """
        INSERT INTO analytics.events (
            event_date,
            event_time,
            event_type,
            session_id,
            page_view_id,
            url,
            pathname,
            referrer,
            user_agent,
            click_x,
            click_y,
            click_type,
            element_tag,
            element_id,
            element_class,
            element_text,
            payload_json
        )
        VALUES
        """,
        [
            (
                event_time.date(),
                event_time,
                event.get("eventType", ""),
                event.get("sessionId", ""),
                event.get("pageViewId", ""),
                event.get("url", ""),
                event.get("pathname", ""),
                event.get("referrer", ""),
                event.get("userAgent", ""),
                event.get("x"),
                event.get("y"),
                event.get("clickType"),
                element.get("tagName"),
                element.get("id"),
                element.get("className"),
                element.get("text"),
                json.dumps(event, ensure_ascii=False),
            )
        ],
    )