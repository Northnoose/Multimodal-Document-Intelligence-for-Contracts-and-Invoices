"""Tests for the Celery worker baseline (ID 7.1).

No real broker is used: Celery is put in eager mode so the task runs in-process, and
the enqueue helper is exercised directly (eager mode) plus with a simulated broker
failure to prove it is best-effort.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import pytest

from app.worker import enqueue as enqueue_module
from app.worker.celery_app import celery_app
from app.worker.enqueue import enqueue_document_processing
from app.worker.tasks import process_document


@pytest.fixture
def eager_celery() -> Iterator[None]:
    """Run tasks synchronously in-process (no broker)."""

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    try:
        yield
    finally:
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False


def test_process_document_returns_id(eager_celery: None) -> None:
    result = process_document.apply(args=("abc123",)).get()
    assert result == "abc123"


def test_process_document_logs_start_and_complete(
    eager_celery: None, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="app.worker.tasks"):
        process_document.apply(args=("doc-42",)).get()
    messages = [r.getMessage() for r in caplog.records]
    assert any("START" in m and "doc-42" in m for m in messages)
    assert any("COMPLETE" in m and "doc-42" in m for m in messages)


def test_enqueue_runs_without_broker(eager_celery: None) -> None:
    # Eager mode means .delay() executes in-process; this must not raise.
    enqueue_document_processing("id-1")


def test_enqueue_swallows_broker_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def _boom(_document_id: str) -> None:
        raise RuntimeError("broker down")

    monkeypatch.setattr(enqueue_module.process_document, "delay", _boom)
    with caplog.at_level(logging.WARNING, logger="app.worker.enqueue"):
        enqueue_document_processing("id-2")  # must not raise
    assert any("Could not enqueue" in r.getMessage() for r in caplog.records)
