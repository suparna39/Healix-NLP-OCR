"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import logger
from app.core.pipeline import initialize_pipeline
from app.api import routes

# Startup/Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting HELIX Medical NLP Engine")
    settings.ensure_directories()
    initialize_pipeline()
    logger.info("Pipeline initialized on startup")

    yield

    # Shutdown
    logger.info("Shutting down HELIX Medical NLP Engine")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Medical NLP Engine for HELIX platform - Extract entities, summarize records, detect risks",
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to known domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "HELIX Medical NLP Engine",
        "version": settings.API_VERSION,
        "status": "operational",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "summarize": "/api/v1/summarize",
            "extract": "/api/v1/extract",
            "models": "/api/v1/models",
        },
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An error occurred",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting HELIX Medical NLP server")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.PORT or 8000),
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
