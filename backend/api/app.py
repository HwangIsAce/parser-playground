"""FastAPI application setup."""
from fastapi import FastAPI

from api.routes import documents, parse


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    raise NotImplementedError
