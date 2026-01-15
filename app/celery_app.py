from celery import Celery
from app.config import settings

celery_app = Celery(
    "user_fetch",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

celery_app.conf.update(
    timezone="Europe/Kyiv",
    enable_utc=True,

    result_serializer="json",
    accept_content=["json"],
    task_serializer="json",

    task_time_limit=300,
    task_soft_time_limit=240,

    task_acks_late=True,
    task_reject_on_worker_lost=True,

    beat_schedule={
        "fetch-users-every-hour":{
            "task": "app.tasks.fetch_and_save_users",
            "schedule": 60.0
        },
    },
)

@celery_app.task
def ping():
    """Тестова задача для перевірки Celery"""
    return "pong"
