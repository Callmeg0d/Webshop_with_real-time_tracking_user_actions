from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis

from app.config import settings
from app.api.products import router as router_products
from app.api.carts import router as router_carts
from app.api.orders import router as router_orders
from app.api.reviews import router as router_reviews
from app.api.users import router_auth as router_users_auth
from app.api.users import router_users as router_users
from app.api.pages import router as router_pages
from app.api.categories import router as router_categories
from app.api.analytics import router as router_analytics
from app.messaging.broker import broker
from app.messaging.handlers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")

    broker.include_router(router)
    await broker.start()

    yield

    await broker.stop()

sentry_sdk.init(
    dsn=settings.SENTRY_URL,
    traces_sample_rate=1.0,
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_users_auth)
app.include_router(router_users)
app.include_router(router_products)
app.include_router(router_carts)
app.include_router(router_orders)
app.include_router(router_reviews)
app.include_router(router_pages)
app.include_router(router_categories)
app.include_router(router_analytics)
# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:7777",
    "http://127.0.0.1:7777",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app)
instrumentator.expose(app)
