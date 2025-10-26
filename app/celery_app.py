from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "photo_management",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks.photo_analysis']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
