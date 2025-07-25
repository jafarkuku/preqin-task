"""
GraphQL Gateway for Investment Platform.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.schema import schema
from app.services import (close_asset_class_client, close_commitment_client,
                          close_investor_client)

logger = logging.getLogger(__name__)


async def close_all_clients():
    """Close all HTTP clients to clean up resources."""
    try:
        await close_investor_client()
        await close_commitment_client()
        await close_asset_class_client()

        logger.info("All HTTP clients closed successfully")

    except Exception as e:
        logger.error("Error closing HTTP clients: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("Starting GraphQL Gateway...")
    yield
    logger.info("Shutting down GraphQL Gateway...")
    await close_all_clients()

app = FastAPI(
    title="GraphQL Gateway",
    version="1.0.0",
    description="Unified GraphQL API for the Investment Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "GraphQL Gateway",
        "version": "1.0.0",
        "status": "running",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql",
        "queries": [
            "investors - List all investors with basic info",
            "investor(id) - Get investor with detailed commitment breakdown"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "GraphQL Gateway",
        "status": "healthy",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
