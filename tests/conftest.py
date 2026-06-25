"""Shared test fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """A TestClient backed by a freshly created application instance."""

    return TestClient(create_app())
