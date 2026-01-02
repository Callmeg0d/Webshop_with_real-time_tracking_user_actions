CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.events
(
    event_date       Date         DEFAULT toDate(event_time),
    event_time       DateTime64(3, 'UTC'),

    event_type       String,
    session_id       String,
    page_view_id     String,

    url              String,
    pathname         String,
    referrer         String,

    user_agent       String,

    click_x          Nullable(Int32),
    click_y          Nullable(Int32),
    click_type       Nullable(String),
    element_tag      Nullable(String),
    element_id       Nullable(String),
    element_class    Nullable(String),
    element_text     Nullable(String),

    -- Сырой JSON всего события, чтобы ничего не потерять
    payload_json     String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_type, event_time, session_id, page_view_id);

