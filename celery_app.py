import os

from celery import Celery


broker_url = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)

result_backend = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/1",
)

celery_app = Celery(
    "pricepulse",
    broker=broker_url,
    backend=result_backend,
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Monterrey",
    enable_utc=True,
)