from qdrant_client.http.models import PointStruct, SparseVector

from app.database.qdrant_client import (
    DENSE_VECTOR_NAME,
    LEXICAL_VECTOR_NAME,
    QdrantStore,
)
from app.schemas.products import IncomingProduct, ProductPayload


def features_to_text(features: dict[str, str] | None) -> str:
    if not features:
        return ""
    return " ".join(f"{k} {v}" for k, v in features.items())


def product_to_searchable_text(product: IncomingProduct) -> str:
    """Текст для индексации: название + начало описания + фичи"""
    name = str(product.get("name") or "").strip()
    description = str(product.get("description") or "").strip()
    features_text = features_to_text(product.get("features"))
    desc_prefix = (description[:400] + "…") if len(description) > 400 else description
    return f"{name} {desc_prefix} {features_text}".strip() or str(product.get("product_id", ""))


def build_payload(product: IncomingProduct) -> ProductPayload:
    # Превращает "сырой" словарь товара (IncomingProduct) в типизированный ProductPayload
    features = product.get("features")
    return ProductPayload(
        product_id=product["product_id"],
        name=str(product.get("name") or ""),
        price=int(product.get("price", 0)),
        product_quantity=int(product.get("product_quantity", 0)),
        description=str(product.get("description") or ""),
        features=features if isinstance(features, dict) else {},
        category_id=int(product.get("category_id", 0)),
        image=str(product.get("image") or ""),
    )

def build_point_for_qdrant(
    product_id: int,
    dense_vector: list[float],
    lexical_vector: SparseVector | None,
    payload: dict[str, object],
) -> PointStruct:
    """Собирает PointStruct для upsert в Qdrant"""
    named_vectors: dict[str, list[float] | SparseVector] = {DENSE_VECTOR_NAME: dense_vector}
    if lexical_vector is not None:
        named_vectors[LEXICAL_VECTOR_NAME] = lexical_vector
    return PointStruct(id=product_id, vector=named_vectors, payload=payload)


class ProductIndexService:
    """Индексация товара в Qdrant по сообщению из Kafka"""

    def __init__(self, qdrant_store: QdrantStore, collection_name: str) -> None:
        self.store = qdrant_store
        self.collection_name = collection_name

    async def index_product(self, product: IncomingProduct) -> None:
        """Строит dense + BM25 векторы и записывает в Qdrant"""
        product_id = product["product_id"]
        #Строит поисковой текст
        text = product_to_searchable_text(product)
        #Считаем dense-эмбеддинг
        vectors = await self.store.embed_texts([text])
        if not vectors:
            return

        dense = vectors[0]
        #Строит lexical sparse вектор
        lexical = await self.store.get_lexical_doc_vector(text)
        await self.store.ensure_collection_exists(
            self.collection_name, vector_size=len(dense)
        )
        #Собирает payload
        payload_dict = dict(build_payload(product))
        point = build_point_for_qdrant(product_id, dense, lexical, payload_dict)
        await self.store.upsert_points(self.collection_name, [point])

    async def remove_product(self, product_id: int) -> None:
        """Удаляет товар из Qdrant"""
        await self.store.delete_points(self.collection_name, [product_id])
