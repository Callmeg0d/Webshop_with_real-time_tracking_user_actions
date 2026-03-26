from fastapi import APIRouter, Depends

from app.dependencies import get_qdrant_store
from app.schemas.recommend import RecommendRequest
from app.services.recommend_service import recommend
from app.database.qdrant_client import QdrantStore

router = APIRouter()


@router.post("/recommend")
async def recommend_endpoint(
    body: RecommendRequest,
    store: QdrantStore = Depends(get_qdrant_store),
) -> list[dict]:

    return await recommend(query=body.query, limit=body.limit, store=store)