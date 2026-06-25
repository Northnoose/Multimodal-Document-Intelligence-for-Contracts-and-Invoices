"""Top-level API router.

Aggregates feature routers into a single ``api_router`` that ``app.main`` mounts.
Future feature routers (documents, extraction, review, export) are included here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)
