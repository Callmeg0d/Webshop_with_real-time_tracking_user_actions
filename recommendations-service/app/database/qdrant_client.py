import asyncio
import json
import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.models import (
    Distance,
    PointIdsList,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from config import settings

from app.services.lexical_bm25 import (
    build_bm25_doc_vector,
    build_bm25_query_vector,
    tokenize_and_stem,
)

# Имена векторов для гибридного поиска (dense + lexical)
DENSE_VECTOR_NAME = "dense"
LEXICAL_VECTOR_NAME = "lexical"

# Порог для dense и lexical
MIN_SCORE_THRESHOLD = 0.11
# Параметр RRF (сглаживание влияния ранга)
K_RRF = 17

def payload_with_scores(payload: dict, dense: float, lex: float, rrf: float) -> dict:
    """Копия payload с полями scores для ответа /recommend"""
    out = dict(payload)
    out["scores"] = {
        "dense": round(float(dense), 6),
        "lexical": round(float(lex), 6),
        "rrf": round(float(rrf), 6),
    }
    return out


def build_lexical_vector(
    text: str, idf_map: dict[str, float], avgdl: float
) -> SparseVector | None:
    """Строит sparse-вектор запроса для BM25"""
    if not idf_map:
        return None
    tokens = tokenize_and_stem(text.strip())
    if not tokens:
        return None
    indices, values = build_bm25_query_vector(tokens, idf_map)
    if not indices:
        return None
    return SparseVector(indices=indices, values=values)


def build_lexical_doc_vector(
    text: str, idf_map: dict[str, float], avgdl: float
) -> SparseVector | None:
    """Строит sparse-вектор документа для BM25"""
    if not idf_map or avgdl <= 0:
        return None
    tokens = tokenize_and_stem(text.strip())
    if not tokens:
        return None
    indices, values = build_bm25_doc_vector(tokens, idf_map, avgdl)
    if not indices:
        return None
    return SparseVector(indices=indices, values=values)


def scored_points_to_map(points: list) -> dict[int, tuple[dict, float]]:
    """Преобразует список точек Qdrant с score в словарь id : (payload, score)"""
    result: dict[int, tuple[dict, float]] = {}
    for p in points:
        pid = p.id
        if isinstance(pid, list):
            pid = pid[0] if pid else 0
        payload = (p.payload or {}) if isinstance(p.payload, dict) else {}
        sc = getattr(p, "score", None)
        result[pid] = (payload, float(sc) if sc is not None else 0.0)
    return result


class QdrantStore:
    def __init__(self) -> None:
        self.host: str = settings.QDRANT_HOST
        self.port: int = settings.QDRANT_EXTERNAL_PORT
        self.client: AsyncQdrantClient | None = None
        self.embedder: HuggingFaceEmbeddings | None = None
        self.idf_map: dict[str, float] | None = None
        self.avgdl: float | None = None

    async def get_client(self) -> AsyncQdrantClient:
        if self.client is None:
            self.client = AsyncQdrantClient(host=self.host, port=self.port)
        return self.client

    async def get_embedder(self) -> HuggingFaceEmbeddings:
        if self.embedder is None:
            self.embedder = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
        return self.embedder

    async def ensure_bm25_stats_loaded(self) -> None:
        """Загружает idf и avgdl из файла"""
        if self.idf_map is not None:
            return
        path = settings.BM25_IDF_PATH
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.idf_map = data.get("idf") or {}
            self.avgdl = float(data.get("avgdl", 0.0))
        except Exception:
            self.idf_map = {}
            self.avgdl = 0.0

    def get_bm25_stats(self) -> tuple[dict[str, float], float]:
        """Возвращает (idf_map, avgdl)"""
        return (self.idf_map or {}, self.avgdl or 0.0)

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
    ) -> None:
        client = await self.get_client()
        await client.create_collection(
            collection_name=collection_name,
            vectors_config={
                DENSE_VECTOR_NAME: VectorParams(size=vector_size, distance=distance),
            },
            sparse_vectors_config={
                LEXICAL_VECTOR_NAME: SparseVectorParams(),
            },
        )

    async def ensure_collection_exists(self, collection_name: str, vector_size: int) -> None:
        client = await self.get_client()
        try:
            await client.get_collection(collection_name)
        except Exception:
            await self.create_collection(collection_name, vector_size)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Dense-эмбеддинг"""
        embedder = await self.get_embedder()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: embedder.embed_documents(texts))

    async def get_lexical_vector(self, text: str) -> SparseVector | None:
        """BM25-вектор запроса"""
        await self.ensure_bm25_stats_loaded()
        idf_map, avgdl = self.get_bm25_stats()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, build_lexical_vector, text, idf_map, avgdl
        )

    async def get_lexical_doc_vector(self, text: str) -> SparseVector | None:
        """BM25-вектор документа для индексации"""
        await self.ensure_bm25_stats_loaded()
        idf_map, avgdl = self.get_bm25_stats()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, build_lexical_doc_vector, text, idf_map, avgdl
        )

    async def upsert_points(
        self,
        collection_name: str,
        points: list[PointStruct],
    ) -> None:
        client = await self.get_client()
        await client.upsert(collection_name=collection_name, points=points)

    async def delete_points(
        self,
        collection_name: str,
        point_ids: list[int],
    ) -> None:
        if not point_ids:
            return
        client = await self.get_client()
        await client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=point_ids),
        )

    async def count_points(self, collection_name: str) -> int:
        """Число точек в коллекции; 0 если коллекции нет или ошибка"""
        log = logging.getLogger(__name__)
        try:
            client = await self.get_client()
            await client.get_collection(collection_name)
            res = await client.count(collection_name=collection_name, exact=True)
            return int(res.count)
        except Exception as e:
            log.debug("count_points(%s): %s", collection_name, e)
            return 0

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        query_text: str,
        limit: int = 10,
        lexical_vec: SparseVector | None = None,
    ) -> list[dict]:
        """
        Гибридный поиск: семантика (dense) + лексика (BM25)
        """
        client = await self.get_client()
        query_filter = None
        fetch_limit = max(min(limit * 12, 100), limit * 2)
        log = logging.getLogger(__name__)
        w_dense = settings.RRF_WEIGHT_DENSE
        w_lexical = settings.RRF_WEIGHT_LEXICAL

        if lexical_vec is None and query_text.strip():
            lexical_vec = await self.get_lexical_vector(query_text)

        if lexical_vec is not None:
            log.info(
                "lexical query vector size=%d (non-zero idf terms)",
                len(lexical_vec.indices) if lexical_vec.indices else 0,
            )
        #Формирование запроса к Qdrant
        rrf_one = qdrant_models.Rrf()
        dense_req = client.query_points(
            collection_name=collection_name,
            prefetch=[
                qdrant_models.Prefetch(
                    query=query_vector,
                    using=DENSE_VECTOR_NAME,
                    limit=fetch_limit,
                    filter=query_filter,
                ),
            ],
            #Qdrant возвращает результат в формате RRF-ранжирования внутри запроса
            query=qdrant_models.RrfQuery(rrf=rrf_one),
            limit=fetch_limit,
            with_payload=True,
            with_vectors=False,
        )
        if lexical_vec is not None:
            lex_req = client.query_points(
                collection_name=collection_name,
                prefetch=[
                    qdrant_models.Prefetch(
                        query=lexical_vec,
                        using=LEXICAL_VECTOR_NAME,
                        limit=fetch_limit,
                        filter=query_filter,
                    ),
                ],
                query=qdrant_models.RrfQuery(rrf=rrf_one),
                limit=fetch_limit,
                with_payload=True,
                with_vectors=False,
            )
            resp_dense, resp_lex = await asyncio.gather(dense_req, lex_req)
        else:
            resp_dense = await dense_req
            resp_lex = None

        dense_by_id = scored_points_to_map(resp_dense.points or [])

        if lexical_vec is None:
            points_with_rrf = [
                (payload, sc, sc, sc)
                for _, (payload, sc) in dense_by_id.items()
            ]
            points_with_rrf.sort(key=lambda x: -x[1])
        else:
            lex_points = (resp_lex.points or []) if resp_lex else []
            log.info(
                "lexical search returned %d points (у остальных lexical_score=0: они не в этом списке)",
                len(lex_points),
            )

            lex_by_id = scored_points_to_map(lex_points)

            # Ранги (1-based)
            rank_dense: dict[int, int] = {}
            for r, pid in enumerate(dense_by_id, start=1):
                rank_dense[pid] = r
            rank_lex: dict[int, int] = {}
            for r, pid in enumerate(lex_by_id, start=1):
                rank_lex[pid] = r

            all_ids = set(dense_by_id) | set(lex_by_id)
            points_with_rrf = []
            for pid in all_ids:
                payload, dense_score = dense_by_id.get(pid, ({}, 0.0))
                _, lex_score = lex_by_id.get(pid, ({}, 0.0))
                rd = rank_dense.get(pid, 9999)
                rl = rank_lex.get(pid, 9999)
                rrf_score = w_dense / (K_RRF + rd) + w_lexical / (K_RRF + rl)
                points_with_rrf.append((payload, dense_score, lex_score, rrf_score))
            points_with_rrf.sort(key=lambda x: -x[3])

        # Полный список кандидатов с рангами и скорами (до порогового фильтра) — для ответа API
        ranking_before_filter: list[dict] = []
        for rank, (payload, dense_score, lex_score, rrf_score) in enumerate(points_with_rrf, start=1):
            product_id = payload.get("product_id")
            ranking_before_filter.append(
                {
                    "rank": rank,
                    "product_id": product_id,
                    "name": str(payload.get("name", "")),
                    "dense_score": float(dense_score),
                    "lexical_score": float(lex_score),
                    "rrf_score": float(rrf_score),
                }
            )
        # Полный список кандидатов до порогового фильтра (не только топ-N) — в INFO для диагностики
        log.info(
            "search full ranking before threshold filter (%d candidates): %s",
            len(ranking_before_filter),
            json.dumps(ranking_before_filter, ensure_ascii=False, default=str),
        )

        # Оставить товары: и dense, и lexical строго выше порога
        points_filtered = [
            x
            for x in points_with_rrf
            if x[1] > MIN_SCORE_THRESHOLD and x[2] > MIN_SCORE_THRESHOLD
        ]
        points_filtered = points_filtered[:limit]

        if points_filtered:
            for rank, (payload, dense_score, lex_score, rrf_score) in enumerate(points_filtered, start=1):
                name = str(payload.get("name", ""))[:60]
                product_id = payload.get("product_id")
                log.info(
                    "search result #%d | product_id=%s | dense_score=%.4f | lexical_score=%.4f | rrf_score=%.4f | name=%s",
                    rank, product_id, dense_score, lex_score, rrf_score, name,
                )
            names = [str((p[0].get("name", ""))[:50]) for p in points_filtered]
            log.info("search summary: names=%s", names)
        else:
            log.info("search summary: no results")

        items_out = [
            payload_with_scores(p, d, l, r)
            for p, d, l, r in points_filtered
        ]
        return items_out
