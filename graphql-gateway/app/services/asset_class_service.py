"""
HTTP clients for communicating with microservices.

Provides clean interfaces for GraphQL resolvers to fetch data from
the investor, commitment, and asset class services.
"""

import logging
from functools import lru_cache
from typing import List, Optional, TypedDict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AssetClassData(TypedDict):
    """Type definition for asset class data from the asset class service."""
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str


class AssetClassClient:
    """HTTP client for the Asset Class Service."""

    def __init__(self):
        """Initialize the asset class service client."""
        self.base_url = settings.asset_class_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_all_asset_classes(self) -> List[AssetClassData]:
        """
        Fetch multiple asset classes by IDs in a single batch request.
        """
        try:
            logger.debug(
                "Fetching all asset classes from asset class service")

            url = f"{self.base_url}/api/asset-classes/"

            response = await self.client.get(url)

            if response.status_code == 200:
                data: list[AssetClassData] = response.json()
                return data
            elif response.status_code == 404:
                logger.debug("Asset classes couldnt be fetched")
                return []
            else:
                logger.error("Error fetching asset classes: HTTP %d - %s",
                             response.status_code, response.text)
                return []

        except httpx.RequestError as e:
            logger.error("Network error fetching asset class: %s",
                         e)
            return []
        except Exception as e:
            logger.error("Unexpected error fetching asset class: %s",
                         e)
            return []

@lru_cache(maxsize=1)
def get_asset_class_client() -> AssetClassClient:
    """
    Get the asset class client instance.
    """
    return AssetClassClient()


async def close_asset_class_client():
    """Close the cached asset class client instance and clear cache."""
    client = get_asset_class_client()
    await client.close()
    get_asset_class_client.cache_clear()
