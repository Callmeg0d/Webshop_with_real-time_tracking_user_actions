from app.database.qdrant_client import QdrantStore
from app.store import store


def get_qdrant_store() -> QdrantStore:
    """Возвращает инстанс QdrantStore"""
    return store
