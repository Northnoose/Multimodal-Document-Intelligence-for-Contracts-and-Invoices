"""Celery worker seam.

Defines a Celery application configured against a Redis broker for future
asynchronous document processing. No tasks are registered and no worker is started
in this phase; this only establishes the integration point.
"""

from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "document_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)
celery_app.conf.task_default_queue = settings.worker_queue_name
celery_app.conf.worker_concurrency = settings.worker_concurrency
