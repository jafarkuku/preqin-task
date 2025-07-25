import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_mongodb_connection, connect_to_mongodb
from app.database import health_check as db_health_check
from app.repositories import get_investor_repository
from app.routers import investors_router
from app.services import event_subscriber

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.

    This ensures database connections are properly managed.
    """
    logger.info("Starting up Investor Service...")
    try:
        await connect_to_mongodb()

        await event_subscriber.connect()

        investor_repository = get_investor_repository()
        event_task = asyncio.create_task(
            event_subscriber.start_listening(investor_repository))
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        raise

    yield

    logger.info("Shutting down Investor Service...")
    event_task.cancel()
    await close_mongodb_connection()
    logger.info("Database connection closed")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A service for managing investors in the investment paltform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

app.include_router(investors_router, prefix="/api")


@app.get("/")
async def root():
    """
    Health check endpoint.
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
        Dict with service health status and database connectivity
    """
    try:
        db_health = await db_health_check()

        is_healthy = db_health["status"] == "healthy"

        health_response = {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": "2024-07-26T10:30:00Z",
            "database": db_health,
            "environment": settings.environment
        }

        return health_response

    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(
            status_code=503, detail=f"Health check failed: {str(e)}") from e


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler with logging."""
    logger.warning("HTTP exception: %s %s - %s",
                   request.method, request.url, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error("Unhandled exception: %s %s - %s",
                 request.method, request.url, exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main.app",
        host=settings.host,
        port=settings.port
    )
