"""Health check route.

Reports that the API process is running. Deliberately does not touch the database,
Redis, or any external dependency so it stays a fast, always-available liveness probe.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service status and application version (no external dependencies)."""

    settings = get_settings()
    return HealthResponse(status="ok", version=settings.app_version)
