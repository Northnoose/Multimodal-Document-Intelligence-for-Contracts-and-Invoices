"""Celery worker seam.

Defines a Celery application configured against a Redis broker for future
asynchronous document processing. No tasks are registered and no worker is started
in this phase; this only establishes the integration point.
"""

from __future__ import annotations

import os

from celery import Celery

broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "document_intelligence",
    broker=broker_url,
    backend=result_backend,
)
