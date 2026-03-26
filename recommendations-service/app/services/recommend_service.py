import asyncio
import logging

from config import settings

from app.database.qdrant_client import QdrantStore

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 2000


def normalize_search_phrase(query: str | None) -> str:
    """Нормализует строку запроса: обрезка пробелов, ограничение длины для эмбеддинга"""
    phrase = (query or "").strip()
    if not phrase:
        return "товары"
    if len(phrase) > MAX_QUERY_LENGTH:
        return phrase[:MAX_QUERY_LENGTH]
    return phrase


async def recommend(
    query: str, limit: int = 3, store: "QdrantStore | None" = None
) -> list[dict]:
    """Текст товара (название, описание, категория, фичи) -> dense + lexical в Qdrant -> список похожих товаров"""

    if store is None:
        store = QdrantStore()
        await store.ensure_bm25_stats_loaded()

    phrase = normalize_search_phrase(query)
    logger.info("search phrase length=%d", len(phrase))

    #dense-вектор для фразы
    vectors_task = store.embed_texts([phrase])

    #sparse BM25-вектор запроса
    lexical_task = store.get_lexical_vector(phrase)

    #Эмбеддер и построение lexical не ждут друг друга
    vectors, lexical_vec = await asyncio.gather(vectors_task, lexical_task)
    if not vectors:
        return []
    query_vector = vectors[0]
    items = await store.search(
        collection_name=settings.DB_COLLECTION_NAME,
        query_vector=query_vector,
        query_text=phrase,
        limit=limit,
        lexical_vec=lexical_vec,
    )
    return items
