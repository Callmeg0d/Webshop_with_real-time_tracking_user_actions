from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    SENTRY_URL: Optional[str] = None

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

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() # type: ignore[call-arg]

