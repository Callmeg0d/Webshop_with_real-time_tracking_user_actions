from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    KAFKA_HOST: str
    KAFKA_INTERNAL_PORT: int

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() # type: ignore[call-arg]


