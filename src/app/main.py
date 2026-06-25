"""FastAPI application entrypoint.

Run locally with::

    uvicorn app.main:app --reload

``create_app`` is a factory so tests can build isolated instances. Configuration is
loaded eagerly here, so a misconfigured environment fails fast at startup with a
clear ``pydantic.ValidationError`` rather than failing later on the first request.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    settings = get_settings()
    app = FastAPI(title=settings.app_title, version=settings.app_version)
    app.include_router(api_router)
    return app


app = create_app()
