import json
from datetime import datetime, timezone

from faststream.kafka import KafkaRouter

from app.analytics.clickhouse_client import get_clickhouse_client

router = KafkaRouter()


async def insert_event_to_clickhouse(event: dict) -> None:
    """Функция для вставки события в ClickHouse."""
    ch = await get_clickhouse_client()

    ts_ms = event.get("timestamp")
    if ts_ms is None:
        event_time = datetime.now(timezone.utc)
    else:
        event_time = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

    element = event.get("element") or {}

    click_x = event.get("x")
    click_y = event.get("y")
    click_type = event.get("clickType")
    element_tag = element.get("tagName")
    element_id = element.get("id")
    element_class = element.get("className")
    element_text = element.get("text")

    event_time_naive = event_time.replace(tzinfo=None)
    event_time_str = event_time_naive.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def escape_sql_string(s):
        if s is None:
            return "NULL"
        return f"'{str(s).replace("'", "''")}'"

    sql = f"""
        INSERT INTO analytics.events (
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
        ) VALUES (
            '{event_time_str}',
            {escape_sql_string(event.get("eventType", ""))},
            {escape_sql_string(event.get("sessionId", ""))},
            {escape_sql_string(event.get("pageViewId", ""))},
            {escape_sql_string(event.get("url", ""))},
            {escape_sql_string(event.get("pathname", ""))},
            {escape_sql_string(event.get("referrer", ""))},
            {escape_sql_string(event.get("userAgent", ""))},
            {click_x if click_x is not None else "NULL"},
            {click_y if click_y is not None else "NULL"},
            {escape_sql_string(click_type)},
            {escape_sql_string(element_tag)},
            {escape_sql_string(element_id)},
            {escape_sql_string(element_class)},
            {escape_sql_string(element_text)},
            {escape_sql_string(json.dumps(event, ensure_ascii=False))}
        )
    """
    
    await ch.execute(sql)


@router.subscriber("clicks_topic", group_id="analytics")
async def handle_click_event(event: dict) -> None:
    await insert_event_to_clickhouse(event)


@router.subscriber("page_views_topic", group_id="analytics")
async def handle_page_view_event(event: dict) -> None:
    await insert_event_to_clickhouse(event)


@router.subscriber("scrolls_topic", group_id="analytics")
async def handle_scroll_event(event: dict) -> None:
    await insert_event_to_clickhouse(event)


@router.subscriber("custom_events_topic", group_id="analytics")
async def handle_custom_event(event: dict) -> None:
    await insert_event_to_clickhouse(event)


@router.subscriber("other_events_topic", group_id="analytics")
async def handle_other_event(event: dict) -> None:
    await insert_event_to_clickhouse(event)

