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


class CommitmentData(TypedDict):
    """Type for basic commitment data from commitment service."""
    id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str
    created_at: str
    updated_at: str


class AssetBreakdownData(TypedDict):
    """Type for asset breakdown data from commitment service."""
    asset_class_id: str
    total_amount: float
    commitment_count: int
    percentage_of_total: float


class CommitmentListResponse(TypedDict):
    """Response from commitment service with total amount."""
    commitments: List[CommitmentData]
    asset_breakdowns: List[AssetBreakdownData]
    total: int
    total_amount: float
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CommitmentClient:
    """HTTP client for the Commitment Service."""

    def __init__(self):
        """Initialize the commitment service client."""
        self.base_url = settings.commitment_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_commitments(
        self,
        investor_id: str = "",
        asset_class_id: Optional[str] = None
    ) -> Optional[CommitmentListResponse]:
        """
        Fetch commitments for a specific investor, optionally filtered by asset class.
        """
        try:
            logger.debug(
                "Fetching commitments for investor %s, asset_class %s",
                investor_id, asset_class_id or "all"
            )

            url = f"{self.base_url}/api/commitments/"

            params = {
                "investor_id": investor_id,
                "page": 1,
                "size": 99
            }

            if asset_class_id:
                params["asset_class_id"] = asset_class_id

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                commitments = data.get("commitments", [])
                logger.debug(
                    "Successfully fetched %d commitments for investor %s",
                    len(commitments), investor_id
                )
                return data
            elif response.status_code == 404:
                logger.debug(
                    "No commitments found for investor: %s", investor_id)
                return {
                    "commitments": [],
                    "asset_breakdowns": [],
                    "total": 0,
                    "total_amount": 0.0,
                    "page": 1,
                    "size": 1000,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                }
            else:
                logger.error(
                    "Error fetching commitments for investor %s: HTTP %d - %s",
                    investor_id, response.status_code, response.text
                )
                return None

        except httpx.RequestError as e:
            logger.error(
                "Network error fetching commitments for investor %s: %s", investor_id, e)
            return None
        except Exception as e:
            logger.error(
                "Unexpected error fetching commitments for investor %s: %s", investor_id, e)
        return None


@lru_cache(maxsize=1)
def get_commitment_client() -> CommitmentClient:
    """
    Get the cached singleton instance of CommitmentClient.

    Returns:
        CommitmentClient: Client for commitment service communication
    """
    return CommitmentClient()


async def close_commitment_client():
    """Close the cached commitment client instance and clear the cache."""
    client = get_commitment_client()
    await client.close()
    get_commitment_client.cache_clear()
