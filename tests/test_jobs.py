"""Tests for the job-status placeholder (ID 8.1).

Covers the DB-free ``JobStatus`` enum and ``JobStatusResponse`` schema, plus the
placeholder ``GET /documents/{document_id}/status`` endpoint. Like the upload tests,
these stay offline: ``get_db_session`` is overridden with an in-memory sqlite session,
storage is pointed at ``tmp_path``, and the enqueue helper is monkeypatched with a spy.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import documents as documents_route
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.domain.documents import JobStatus, JobStatusResponse
from app.main import create_app


def test_job_status_members_and_values() -> None:
    assert JobStatus.QUEUED.value == "queued"
    assert JobStatus.PROCESSING.value == "processing"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
    assert {status.value for status in JobStatus} == {
        "queued",
        "processing",
        "completed",
        "failed",
    }


def test_job_status_response_round_trips() -> None:
    document_id = uuid.uuid4()
    schema = JobStatusResponse.model_validate(
        {"document_id": document_id, "status": "queued"}
    )
    assert schema.document_id == document_id
    assert schema.status is JobStatus.QUEUED


@pytest.fixture
def sqlite_sessionmaker() -> Iterator[sessionmaker[Session]]:
    """An in-memory sqlite session factory with the schema created."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def enqueue_spy(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace the route's enqueue helper with a spy so no broker is touched."""

    calls: list[str] = []
    monkeypatch.setattr(
        documents_route, "enqueue_document_processing", lambda doc_id: calls.append(doc_id)
    )
    return calls


@pytest.fixture
def app_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sqlite_sessionmaker: sessionmaker[Session],
) -> Iterator[TestClient]:
    """A TestClient whose DB dependency uses sqlite and storage uses ``tmp_path``."""

    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    get_settings.cache_clear()

    def _override() -> Iterator[Session]:
        session = sqlite_sessionmaker()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db_session] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_status_for_uploaded_document_returns_queued(
    app_client: TestClient, enqueue_spy: list[str]
) -> None:
    upload = app_client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert upload.status_code == 201
    document_id = upload.json()["id"]

    response = app_client.get(f"/documents/{document_id}/status")
    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == JobStatus.QUEUED.value


def test_status_for_unknown_document_returns_404(app_client: TestClient) -> None:
    response = app_client.get(f"/documents/{uuid.uuid4()}/status")
    assert response.status_code == 404


def test_status_for_malformed_id_returns_422(app_client: TestClient) -> None:
    response = app_client.get("/documents/not-a-uuid/status")
    assert response.status_code == 422
