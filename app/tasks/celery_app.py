import os

from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

celery = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}",
    include=["app.tasks.tasks"]
)