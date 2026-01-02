from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.api.orders import router as router_orders
from app.messaging.broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app = FastAPI(lifespan=lifespan)

app.include_router(router_orders)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app)
instrumentator.expose(app)

