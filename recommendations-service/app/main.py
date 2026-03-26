import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.recommendations import router
from app.store import store
from app.messaging.broker import broker
from app.messaging.handlers import router as kafka_router
from app.services.product_service_bootstrap import bootstrap_qdrant_from_product_service_if_empty

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("aiokafka").setLevel(logging.WARNING)
logging.getLogger("faststream").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.get_embedder()
    await store.ensure_bm25_stats_loaded()
    await bootstrap_qdrant_from_product_service_if_empty(store)
    broker.include_router(kafka_router)
    await broker.start()
    yield
    await broker.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(router)