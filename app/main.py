from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis

from app.config import settings
from app.images.router import router as router_images
from app.orders.router import router as router_orders
from app.pages.router import router as router_pages
from app.products.router import router as router_products
from app.reviews.router import router as router_reviews
from app.shopping_carts.router import router as router_shopping_carts
from app.users.router import router_auth as router_users_auth
from app.users.router import router_users as router_users
from app.websockets import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


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
app.include_router(router_orders)
app.include_router(router_shopping_carts)
app.include_router(router_reviews)
app.include_router(router_pages)
app.include_router(router_images)
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app)
instrumentator.expose(app)
