from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from shared import setup_logging

from app.config import settings
from app.api.pages import router as router_pages
from app.api.gateway import router as router_gateway


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# sentry_sdk.init(
#     dsn=settings.SENTRY_URL,
#     traces_sample_rate=1.0,
#     _experiments={
#         "continuous_profiling_auto_start": True,
#     },
# )
setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router_pages)
app.include_router(router_gateway)

# CORS для фронтенда
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
        "X-User-Id",
    ],
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app)
instrumentator.expose(app)

