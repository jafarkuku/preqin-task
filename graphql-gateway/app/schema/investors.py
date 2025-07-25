"""
GraphQL Schema for Investment Platform.

Defines the core queries:
1. investors - List all investors with metadata
"""
import logging
from typing import List

import strawberry

from app.services import get_investor_client

logger = logging.getLogger(__name__)


@strawberry.type
class InvestorDetail:
    """Basic investor information for GraphQL responses."""
    id: str
    name: str
    investor_type: str
    country: str
    date_added: str
    commitment_count: int
    total_commitment_amount: float
    created_at: str
    updated_at: str


@strawberry.type
class InvestorList:
    """Paginated list of investors with metadata (matches investor service response)."""
    investors: List[InvestorDetail]
    total_commitment_amount: float
    total: int
    page: int
    size: int
    total_pages: int


@strawberry.type
class InvestorQueries:
    """Investor-related GraphQL queries."""

    @strawberry.field
    async def investors(self, page: int = 1, size: int = 20) -> InvestorList:
        """
        Get paginated list of all investors with metadata.
        """
        try:
            logger.info("Fetching investors list (page: %d, size: %d)",
                        page, size)

            investor_client = get_investor_client()
            response = await investor_client.get_all_investors(
                page,
                size
            )

            if not response:
                logger.warning("Invalid response from investor service")
                return InvestorList(
                    investors=[],
                    total_commitment_amount=0.0,
                    total=0,
                    page=page,
                    size=size,
                    total_pages=0
                )

            investors_summary = [
                InvestorDetail(**investor)
                for investor in response["investors"]
            ]

            investors_list = InvestorList(
                investors=investors_summary,
                total_commitment_amount=response.get(
                    "total_commitment_amount", 0.0),
                total=response.get("total", 0),
                page=response.get("page", page),
                size=response.get("size", size),
                total_pages=response.get("total_pages", 0)
            )

            logger.info("Successfully returned %d investors with metadata", len(
                investors_summary))
            return investors_list

        except Exception as e:
            logger.error("Error fetching investors: %s", e)
            return InvestorList(
                investors=[],
                total_commitment_amount=0.0,
                total=0,
                page=page,
                size=size,
                total_pages=0
            )
