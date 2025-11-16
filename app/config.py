from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    SENTRY_URL: Optional[str] = None

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int

    KAFKA_HOST: str
    KAFKA_PORT: int

    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:'
                f'{self.DB_PASS}@{self.DB_HOST}:'
                f'{self.DB_PORT}/{self.DB_NAME}')

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

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() # type: ignore[call-arg]
