from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    QDRANT_HOST: str
    QDRANT_EXTERNAL_PORT: int
    QDRANT_INTERNAL_PORT: int
    DB_COLLECTION_NAME: str
    EMBEDDING_MODEL_NAME: str
    RRF_WEIGHT_DENSE: float = 0.35
    RRF_WEIGHT_LEXICAL: float = 0.65
    BM25_IDF_PATH: str
    KAFKA_HOST: str
    KAFKA_PORT: int

    PRODUCT_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()