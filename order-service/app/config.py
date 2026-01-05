from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_INTERNAL_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    CART_SERVICE_URL: str  # URL для вызова cart-service
    PRODUCT_SERVICE_URL: str  # URL для вызова product-service
    USER_SERVICE_URL: str  # URL для вызова user-service
    KAFKA_HOST: str
    KAFKA_INTERNAL_PORT: int

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:'
                f'{self.DB_PASS}@{self.DB_HOST}:'
                f'{self.DB_INTERNAL_PORT}/{self.DB_NAME}')

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore[call-arg]

