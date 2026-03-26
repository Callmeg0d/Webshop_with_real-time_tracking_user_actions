from config import settings

from app.database.qdrant_client import QdrantStore
from app.services.product_index_service import ProductIndexService

store = QdrantStore()
product_index_service = ProductIndexService(store, settings.DB_COLLECTION_NAME)
