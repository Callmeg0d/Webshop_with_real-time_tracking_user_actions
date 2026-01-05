from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared import setup_logging

from app.config import settings
from app.api.users import router_auth as router_users_auth
from app.api.users import router_users as router_users
from app.messaging.broker import broker
from app.messaging.handlers import router as kafka_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker.include_router(kafka_router)
    await broker.start()

    yield

    await broker.stop()


# sentry_sdk.init(
#     dsn=settings.SENTRY_URL,
#     traces_sample_rate=1.0,
#     _experiments={
#         "continuous_profiling_auto_start": True,
#     },
# )
setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

app = FastAPI(lifespan=lifespan)

app.include_router(router_users_auth)
app.include_router(router_users)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app)
instrumentator.expose(app)

