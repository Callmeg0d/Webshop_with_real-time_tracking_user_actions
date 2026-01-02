from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    KAFKA_HOST: str
    KAFKA_PORT: int

    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() # type: ignore[call-arg]

