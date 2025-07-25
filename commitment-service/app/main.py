"""
Commitment Service FastAPI application.

This module defines the main FastAPI application for the Commitment Service,
following the same patterns as the Investor Service.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_database_connection, connect_to_database
from app.database import health_check as db_health_check
from app.routers import commitments_router
from app.services import event_publisher

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    logger.info("Starting up Commitment Service...")
    try:
        await connect_to_database()
        await event_publisher.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        raise

    yield

    logger.info("Shutting down Commitment Service...")
    await close_database_connection()
    await event_publisher.disconnect()
    logger.info("All connections closed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A service for managing investment commitments in the investment platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

app.include_router(commitments_router, prefix="/api")


@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", summary="Health check", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dict with service health status, database connectivity, and external service status
    """
    try:
        db_health = await db_health_check()

        is_db_healthy = db_health["status"] == "healthy"
        is_healthy = is_db_healthy

        health_response = {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_health,
            "environment": settings.environment
        }

        if is_healthy:
            return health_response
        else:
            raise HTTPException(
                status_code=503,
                detail=health_response
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        ) from e


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler with logging."""
    logger.error("HTTP exception: %s %s - %s",
                 request.method, request.url, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
