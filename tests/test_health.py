"""Tests for the /health endpoint (backlog item 2.2)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import __version__


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
