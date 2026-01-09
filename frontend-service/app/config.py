from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #SENTRY_URL: Optional[str] = None

    # URLs микросервисов
    USER_SERVICE_URL: str
    PRODUCT_SERVICE_URL: str
    CART_SERVICE_URL: str
    ORDER_SERVICE_URL: str
    REVIEW_SERVICE_URL: str
    ANALYTICS_SERVICE_URL: str

    # Для аутентификации через cookies
    SECRET_KEY: str
    ALGORITHM: str

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore[call-arg]

