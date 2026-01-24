from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    KAFKA_HOST: str
    KAFKA_INTERNAL_PORT: int
    KAFKA_EXTERNAL_PORT: int

    CLICKHOUSE_HOST: str
    CLICKHOUSE_INTERNAL_PORT: int
    CLICKHOUSE_EXTERNAL_PORT: int
    CLICKHOUSE_INTERNAL_NATIVE_PORT: int
    CLICKHOUSE_EXTERNAL_NATIVE_PORT: int

    ANALYTICS_SERVICE_EXTERNAL_PORT: int
    ANALYTICS_SERVICE_INTERNAL_PORT: int

    GRAFANA_EXTERNAL_PORT: int

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore[call-arg]

