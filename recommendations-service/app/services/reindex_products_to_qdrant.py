import json
import logging

from qdrant_client.http.models import SparseVector

from app.database.qdrant_client import QdrantStore
from app.services.lexical_bm25 import (
    build_bm25_doc_vector,
    compute_corpus_bm25_stats,
    tokenize_and_stem,
)
from app.services.product_index_service import (
    build_payload,
    build_point_for_qdrant,
    product_to_searchable_text,
)
from config import settings

logger = logging.getLogger(__name__)


async def reindex_products_to_qdrant(products: list[dict], store: QdrantStore) -> int:
    """
    По всему переданному списку products заново считает глобальную BM25-статистику (IDF, средняя длина документа),
    перезаписывает idf.json, затем для каждого товара строит dense и lexical (sparse) векторы
    и делает один массовый upsert в Qdrant.
    """
    if not products:
        return 0

    collection = settings.DB_COLLECTION_NAME
    #Для каждого товара собирает строку (название, описание, фичи)
    texts = [product_to_searchable_text(p) for p in products]
    logger.info("reindex_qdrant: токенизация и BM25 по %d товарам", len(texts))

    docs_tokenized = [tokenize_and_stem(t) for t in texts]
    #Считает idf_map и avgdl по всем документам
    idf_map, avgdl, _ = compute_corpus_bm25_stats(docs_tokenized)

    idf_path = settings.BM25_IDF_PATH
    with open(idf_path, "w", encoding="utf-8") as f:
        json.dump({"idf": idf_map, "avgdl": avgdl, "N": len(products)}, f, ensure_ascii=False)
    logger.info(
        "reindex_qdrant: сохранён %s (avgdl=%.2f, терминов=%d)",
        idf_path,
        avgdl,
        len(idf_map),
    )

    # После записи файла инстанс store перечитывает статистику
    store.idf_map = None
    store.avgdl = None
    await store.ensure_bm25_stats_loaded()

    logger.info("reindex_qdrant: dense эмбеддинги...")
    vectors = await store.embed_texts(texts)
    if not vectors:
        logger.error("reindex_qdrant: не удалось получить dense эмбеддинги")
        return 0

    vector_size = len(vectors[0])
    await store.ensure_collection_exists(collection, vector_size=vector_size)

    points = []
    for i, p in enumerate(products):
        idx, val = build_bm25_doc_vector(docs_tokenized[i], idf_map, avgdl)
        #Lexical: sparse BM25 по уже посчитанным idf_map/avgdl и токенам документа i
        #Dense: vectors[i] для того же текста
        lexical = SparseVector(indices=idx, values=val) if idx else None
        point = build_point_for_qdrant(
            p["product_id"],
            vectors[i],
            lexical,
            dict(build_payload(p)),
        )
        points.append(point)

    await store.upsert_points(collection, points)
    logger.info("reindex_qdrant: в Qdrant загружено точек: %d", len(points))
    return len(points)

