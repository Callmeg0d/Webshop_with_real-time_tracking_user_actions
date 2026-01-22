from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]

    DB_HOST: str
    DB_INTERNAL_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    USER_SERVICE_URL: str  # URL для вызова user-service
    KAFKA_HOST: str
    KAFKA_INTERNAL_PORT: int

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    @property
    def DATABASE_URL(self):
        """Возвращает URL БД в зависимости от MODE"""
        if self.MODE == "TEST":
            return self.TEST_DATABASE_URL
        return (f'postgresql+asyncpg://{self.DB_USER}:'
                f'{self.DB_PASS}@{self.DB_HOST}:'
                f'{self.DB_INTERNAL_PORT}/{self.DB_NAME}')

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.TEST_DB_USER}:'
                f'{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:'
                f'{self.TEST_DB_PORT}/{self.TEST_DB_NAME}')

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore[call-arg]

