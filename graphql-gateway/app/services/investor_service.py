"""
HTTP clients for communicating with microservices.

Provides clean interfaces for GraphQL resolvers to fetch data from
the investor, commitment, and asset class services.
"""

import logging
from functools import lru_cache
from typing import Optional, TypedDict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class InvestorData(TypedDict):
    """Type definition for investor data from the investor service."""
    id: str
    name: str
    investor_type: str
    country: str
    date_added: str
    commitment_count: int
    total_commitment_amount: float
    created_at: str
    updated_at: str


class InvestorListResponse(TypedDict):
    """Model for paginated investor list responses."""
    investors: list[InvestorData]
    total_commitment_amount: float
    total: int
    page: int
    size: int
    total_pages: int


class InvestorClient:
    """HTTP client for the Investor Service."""

    def __init__(self):
        """Initialize the investor service client."""
        self.base_url = settings.investor_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_all_investors(self, page: int, size: int) -> Optional[InvestorListResponse]:
        """
        Fetch all investors from the investor service.

        Returns:
            List of investor dictionaries or None if error
        """
        try:
            logger.debug("Fetching all investors from investor service")

            url = f"{self.base_url}/api/investors/"
            params = {
                "page": page,
                "size": size
            }

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                logger.debug("Successfully fetched %d investors (total: %d)",
                             len(data.get("investors", [])), data.get("total", 0))
                return data
            else:
                logger.error("Error fetching investors: HTTP %d - %s",
                             response.status_code, response.text)
                return None

        except httpx.RequestError as e:
            logger.error("Network error fetching investors: %s", e)
            return None
        except Exception as e:
            logger.error("Unexpected error fetching investors: %s", e)
            return None

    async def get_investor(self, investor_id: str) -> Optional[InvestorData]:
        """
        Fetch a specific investor by ID.

        Args:
            investor_id: Investor identifier

        Returns:
            Investor dictionary or None if not found/error
        """
        try:
            logger.debug(
                "Fetching investor %s from investor service", investor_id)

            url = f"{self.base_url}/api/investors/{investor_id}"
            response = await self.client.get(url)

            if response.status_code == 200:
                investor_data = response.json()
                logger.debug("Successfully fetched investor: %s",
                             investor_data.get("name"))
                return investor_data
            elif response.status_code == 404:
                logger.debug("Investor not found: %s", investor_id)
                return None
            else:
                logger.error("Error fetching investor %s: HTTP %d - %s",
                             investor_id, response.status_code, response.text)
                return None

        except httpx.RequestError as e:
            logger.error("Network error fetching investor %s: %s",
                         investor_id, e)
            return None
        except Exception as e:
            logger.error(
                "Unexpected error fetching investor %s: %s", investor_id, e)
            return None


@lru_cache(maxsize=1)
def get_investor_client() -> InvestorClient:
    """
    Get the cached singleton instance of InvestorClient.

    Returns:
        InvestorClient: Client for investor service communication
    """
    return InvestorClient()


async def close_investor_client():
    """Close the cached investor client instance and clear the cache."""
    client = get_investor_client()
    await client.close()
    get_investor_client.cache_clear()
