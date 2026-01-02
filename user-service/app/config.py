from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DB_HOST: str
    DB_INTERNAL_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_HOST: str
    REDIS_INTERNAL_PORT: int

    KAFKA_HOST: str
    KAFKA_INTERNAL_PORT: int

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:'
                f'{self.DB_PASS}@{self.DB_HOST}:'
                f'{self.DB_INTERNAL_PORT}/{self.DB_NAME}')

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore[call-arg]

