"""FastAPI application setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import documents, parse, jobs
from config import settings


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
    
    return app
