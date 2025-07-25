"""
Ingestion Service for Investment Platform.

This microservice handles bulk data ingestion from CSV files,
efficiently processing data in batches to populate other services.

On startup, it automatically processes data.csv if found in the root directory.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pandas as pd
from fastapi import FastAPI

from app.config import settings
from app.services.data_processor import DataProcessor

logger = logging.getLogger(__name__)

# Global variable to track startup ingestion
startup_ingestion_completed = False
startup_ingestion_result = None


async def startup_data_ingestion():
    """
    Automatically ingest data.csv on startup if it exists.
    """
    global startup_ingestion_completed, startup_ingestion_result

    try:
        # Look for data.csv in the root directory
        csv_path = Path("/app/data.csv")
        if not csv_path.exists():
            # Try local development path
            csv_path = Path("../data.csv")
        if not csv_path.exists():
            # Try current directory
            csv_path = Path("./data.csv")

        if not csv_path.exists():
            logger.info("No data.csv found for startup ingestion")
            startup_ingestion_completed = True
            return

        logger.info(
            "Found data.csv, starting automatic ingestion on startup...")

        await wait_for_services()

        # Process the CSV file
        df = pd.read_csv(csv_path)
        logger.info("Loaded CSV with %d rows", len(df))

        # Create batch processor and process data
        processor = DataProcessor()
        job_id = "startup-ingestion"

        result = await processor.process_dataframe(df, job_id)

        startup_ingestion_result = result
        startup_ingestion_completed = True

        if result.get('status') == 'completed':
            logger.info("Startup ingestion completed successfully:")
            logger.info("Asset classes created: %s",
                        result.get('asset_classes_created', 0))
            logger.info("Investors created: %s",
                        result.get('investors_created', 0))
            logger.info("Commitments created: %s",
                        result.get('commitments_created', 0))
        else:
            logger.error("Startup ingestion failed: %s", result.get('error'))

    except Exception as e:
        logger.error("💥 Error during startup ingestion: %s", e)
        startup_ingestion_completed = True
        startup_ingestion_result = {
            'status': 'failed',
            'error': str(e)
        }


async def wait_for_services(max_retries: int = 30, delay: float = 2.0):
    """
    Wait for all required services to be ready.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    services = {
        "Asset Class Service": f"{settings.asset_class_service_url}/health",
        "Investor Service": f"{settings.investor_service_url}/health",
        "Commitment Service": f"{settings.commitment_service_url}/health"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(max_retries):
            all_ready = True

            for service_name, health_url in services.items():
                try:
                    response = await client.get(health_url)
                    if response.status_code == 200:
                        logger.debug("%s is ready", service_name)
                    else:
                        logger.debug("⏳ %s not ready (HTTP %d)",
                                     service_name, response.status_code)
                        all_ready = False
                except Exception as e:
                    logger.debug("⏳ %s not ready: %s", service_name, e)
                    all_ready = False

            if all_ready:
                logger.info(
                    "All services are ready, proceeding with ingestion")
                return

            if attempt < max_retries - 1:
                logger.info("⏳ Waiting for services to be ready... (attempt %d/%d)",
                            attempt + 1, max_retries)
                await asyncio.sleep(delay)

        raise Exception(f"Services not ready after {max_retries} attempts")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info("Starting Ingestion Service...")

    import asyncio
    asyncio.create_task(startup_data_ingestion())

    yield
    logger.info("Shutting down Ingestion Service...")


app = FastAPI(
    title="Ingestion Service",
    version="1.0.0",
    description="Efficient bulk data ingestion for the investment platform with automatic startup seeding",
    lifespan=lifespan
)


@app.get(
    "/api/startup-status",
    summary="Get startup ingestion status",
    description="Check if the automatic startup data ingestion has completed."
)
async def get_startup_status():
    """
    Get the status of automatic startup data ingestion.

    Returns:
        Dict with startup ingestion status and results
    """
    global startup_ingestion_completed, startup_ingestion_result

    if not startup_ingestion_completed:
        return {
            "status": "in_progress",
            "message": "Startup data ingestion is still in progress"
        }

    if startup_ingestion_result:
        return {
            "status": "completed",
            "message": "Startup data ingestion completed",
            "results": startup_ingestion_result
        }
    else:
        return {
            "status": "completed",
            "message": "No data.csv found for startup ingestion"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global startup_ingestion_completed

    return {
        "service": "Ingestion Service",
        "status": "healthy",
        "version": "1.0.0",
        "startup_ingestion_completed": startup_ingestion_completed
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
