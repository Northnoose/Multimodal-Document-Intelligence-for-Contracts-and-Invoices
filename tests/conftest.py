"""Shared test fixtures."""

from __future__ import annotations

import os
from collections.abc import Iterator

# The required config must exist before ``app.main`` is imported below, because
# that import eagerly builds ``app = create_app()`` (which loads Settings). These
# are test-scoped, credential-free localhost URLs that are never connected to.
# ``setdefault`` leaves any real developer environment untouched.
_TEST_DATABASE_URL = "postgresql+psycopg://localhost:5432/document_intelligence_test"
_TEST_REDIS_URL = "redis://localhost:6379/1"
os.environ.setdefault("DATABASE_URL", _TEST_DATABASE_URL)
os.environ.setdefault("REDIS_URL", _TEST_REDIS_URL)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(autouse=True)
def _required_config(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Inject the required config so the suite is hermetic and secret-free.

    ``database_url`` / ``redis_url`` are required, so tests must supply them.
    These credential-free localhost URLs are never connected to (``/health`` is
    dependency-free). The ``get_settings`` cache is cleared before and after each
    test so overrides take effect deterministically, regardless of any developer
    ``.env``.
    """

    monkeypatch.setenv("DATABASE_URL", _TEST_DATABASE_URL)
    monkeypatch.setenv("REDIS_URL", _TEST_REDIS_URL)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    """A TestClient backed by a freshly created application instance."""

    return TestClient(create_app())
