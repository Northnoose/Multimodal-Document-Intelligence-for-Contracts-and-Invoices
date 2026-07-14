"""Tests for the document model, response schema, and upload endpoint (IDs 5.1/5.2).

These stay free of live PostgreSQL and Redis: the ``get_db_session`` dependency is
overridden with an in-memory sqlite session, storage is pointed at ``tmp_path``, and
the enqueue helper is monkeypatched with a spy so no broker is touched.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import documents as documents_route
from app.core.config import get_settings
from app.db.base import Base
from app.db.models import Document
from app.db.session import get_db_session
from app.domain.documents import DocumentResponse, DocumentStatus, DocumentType
from app.main import create_app


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
    """Replace the route's enqueue helper with a spy capturing its arguments."""

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


def test_upload_pdf_returns_201(app_client: TestClient, enqueue_spy: list[str]) -> None:
    response = app_client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["status"] == DocumentStatus.UPLOADED.value
    assert body["document_type"] == DocumentType.UNKNOWN.value
    assert body["original_filename"] == "invoice.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["storage_path"].startswith("originals/")
    assert body["upload_timestamp"]
    assert enqueue_spy == [body["id"]]


def test_upload_text_plain_returns_201(
    app_client: TestClient, enqueue_spy: list[str]
) -> None:
    response = app_client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["content_type"] == "text/plain"


def test_upload_unsupported_type_returns_415(
    app_client: TestClient, enqueue_spy: list[str]
) -> None:
    response = app_client.post(
        "/documents/upload",
        files={"file": ("archive.zip", b"PK\x03\x04", "application/zip")},
    )
    assert response.status_code == 415
    assert enqueue_spy == []


def test_upload_missing_file_returns_422(app_client: TestClient) -> None:
    response = app_client.post("/documents/upload")
    assert response.status_code == 422


def test_upload_unsafe_filename_is_sanitised(
    app_client: TestClient, enqueue_spy: list[str], tmp_path: Path
) -> None:
    response = app_client.post(
        "/documents/upload",
        files={"file": ("../../etc/passwd", b"data", "text/plain")},
    )
    assert response.status_code == 201
    body = response.json()
    assert ".." not in body["storage_path"]
    assert not body["storage_path"].startswith("/")
    assert body["storage_path"].startswith("originals/")
    # The raw name is preserved as the display string only.
    assert body["original_filename"] == "../../etc/passwd"


def test_uploaded_file_stored_under_root(
    app_client: TestClient, enqueue_spy: list[str], tmp_path: Path
) -> None:
    response = app_client.post(
        "/documents/upload",
        files={"file": ("report.pdf", b"%PDF fake bytes", "application/pdf")},
    )
    assert response.status_code == 201
    storage_path = response.json()["storage_path"]
    stored = tmp_path.resolve() / storage_path
    assert stored.is_file()
    assert stored.read_bytes() == b"%PDF fake bytes"


def test_document_response_from_orm() -> None:
    doc = Document(
        id=uuid.uuid4(),
        original_filename="a.pdf",
        content_type="application/pdf",
        storage_path="originals/x_a.pdf",
        status=DocumentStatus.UPLOADED.value,
        document_type=DocumentType.UNKNOWN.value,
        upload_timestamp=datetime.now(timezone.utc),
    )
    schema = DocumentResponse.model_validate(doc)
    assert schema.status is DocumentStatus.UPLOADED
    assert schema.document_type is DocumentType.UNKNOWN
    assert schema.original_filename == "a.pdf"
