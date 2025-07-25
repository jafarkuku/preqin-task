from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_to_mongodb, close_mongodb_connection
from app.routers import asset_classes_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan context manager for FastAPI.
    """
    await connect_to_mongodb()

    yield

    await close_mongodb_connection()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A service for managing asset classes in the investment paltform",
    lifespan=lifespan
)

app.include_router(asset_classes_router, prefix='/api')


@app.get("/")
async def root():
    """
    Health check endpoint.
    """

    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
