"""FastAPI application setup."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import documents, parse, jobs, chunking
from config import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Forge Playground API",
        version="1.0.0",
        description="Document parsing and extraction playground API",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        documents.router,
        prefix="/api/v1",
        tags=["documents"],
    )
    app.include_router(
        parse.router,
        prefix="/api/v1",
        tags=["parse"],
    )
    app.include_router(
        jobs.router,
        prefix="/api/v1",
        tags=["jobs"],
    )
    app.include_router(
        chunking.router,
        prefix="/api/v1",
        tags=["chunking"],
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Forge Playground API",
            "version": "1.0.0",
        }
    
    # Health check
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Ensure every unhandled exception returns JSON with detail (no HTML 500)."""
        logger.exception("Unhandled exception: %s", exc)
        msg = str(exc).strip() or type(exc).__name__
        detail = f"{type(exc).__name__}: {msg}" if msg != type(exc).__name__ else msg
        return JSONResponse(
            status_code=500,
            content={"detail": detail},
        )

    return app
