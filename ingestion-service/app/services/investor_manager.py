"""
Investor management for ingestion service.

Handles creating investors.
"""

import asyncio
import logging
from typing import Dict, List, TypedDict

import httpx

logger = logging.getLogger(__name__)


class InvestorData(TypedDict):
    """Shape of investor data passed to bulk_create_investors."""
    name: str
    investor_type: str
    country: str
    date_added: str


class CreatedInvestorResponse(TypedDict):
    """Response from investor service when creating an investor."""
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
    """Response from investor service list endpoint."""
    investors: List[CreatedInvestorResponse]
    total_commitment_amount: float
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class InvestorManager:
    """Manages investor creation and retrieval."""

    def __init__(self, client: httpx.AsyncClient, investor_url: str) -> None:
        self.client = client
        self.investor_url = investor_url

    async def bulk_create_investors(self, investors: Dict[str, InvestorData]) -> Dict[str, str]:
        """
        Create investors and return name->ID mapping.
        """
        if not investors:
            return {}

        logger.info(
            "Processing %d investors (create or fetch existing)", len(investors))

        try:
            # Step 1: Check which investors already exist
            name_to_id = await self._fetch_existing_investors(list(investors.keys()))

            # Step 2: Only create investors that don't exist
            new_investors = {
                name: data for name, data in investors.items()
                if name not in name_to_id
            }

            if new_investors:
                logger.info("Creating %d new investors (found %d existing)",
                            len(new_investors), len(name_to_id))

                bulk_mapping = await self._bulk_create_investors(new_investors)
                name_to_id.update(bulk_mapping)
            else:
                logger.info(
                    "All %d investors already exist, no creation needed", len(investors))

            # Step 3: Log the final mapping for debugging
            logger.info("Final investor mapping: %d total", len(name_to_id))
            logger.debug("Investor name->ID mapping: %s",
                         {name: id[:8] + "..." for name, id in list(name_to_id.items())[:5]})

            return name_to_id

        except Exception as e:
            logger.error("Error in investor processing: %s", e)
            return {}

    async def _fetch_existing_investors(self, investor_names: List[str]) -> Dict[str, str]:
        """
        Fetch existing investors by name and return name to ID mapping
        """
        name_to_id = {}

        try:
            # Get all investors with pagination to handle large datasets
            page = 1
            all_existing_investors: List[CreatedInvestorResponse] = []

            while True:
                response = await self.client.get(
                    f"{self.investor_url}/api/investors/?page={page}&size=100"
                )

                if response.status_code == 200:
                    data: InvestorListResponse = response.json()
                    investors = data.get('investors', [])
                    all_existing_investors.extend(investors)

                    # Check if we have more pages
                    if not data.get('has_next', False):
                        break
                    page += 1
                else:
                    logger.error("Failed to fetch existing investors: HTTP %d - %s",
                                 response.status_code, response.text)
                    break

            logger.debug("Fetched %d existing investors from service",
                         len(all_existing_investors))

            for investor in all_existing_investors:
                if investor['name'] in investor_names:
                    name_to_id[investor['name']] = investor['id']
                    logger.debug("Found existing investor: %s -> %s",
                                 investor['name'], investor['id'])

            logger.info("Found %d existing investors out of %d requested",
                        len(name_to_id), len(investor_names))

        except Exception as e:
            logger.error("Error fetching existing investors: %s", e)

        return name_to_id

    async def _bulk_create_investors(self, investors: Dict[str, InvestorData]) -> Dict[str, str]:
        """
        Create investors using the bulk endpoint for maximum efficiency.
        """
        if not investors:
            return {}

        name_to_id = {}

        try:
            investors_list: List[InvestorData] = []
            name_order: List[str] = []

            for name, data in investors.items():
                investors_list.append(data)
                name_order.append(name)

            logger.info(
                "Bulk creating %d investors in single request", len(investors_list))

            response = await self.client.post(
                f"{self.investor_url}/api/investors/bulk-create",
                json=investors_list
            )

            if response.status_code == 200:
                created_investors: List[CreatedInvestorResponse] = response.json(
                )

                if isinstance(created_investors, list):
                    for i, created_investor in enumerate(created_investors):
                        if i < len(name_order):
                            name = name_order[i]
                            investor_id = created_investor.get('id')
                            if investor_id:
                                name_to_id[name] = investor_id
                                logger.debug("Bulk created investor: %s -> %s",
                                             name, investor_id)

                logger.info("Successfully bulk created %d/%d investors",
                            len(name_to_id), len(investors))

            else:
                logger.error("Bulk create failed: HTTP %d - %s",
                             response.status_code, response.text)

                logger.warning("Falling back to individual creates...")
                name_to_id = await self._create_investors_individually_fallback(investors)

        except Exception as e:
            logger.error("Error in bulk create: %s", e)

            logger.warning(
                "Falling back to individual creates due to error...")
            name_to_id = await self._create_investors_individually_fallback(investors)

        return name_to_id

    async def _create_single_investor(self, name: str, data: InvestorData) -> tuple[str, str | None]:
        """Create a single investor and return (name, id) tuple."""
        try:
            logger.debug("Creating investor concurrently: %s", name)

            response = await self.client.post(
                f"{self.investor_url}/api/investors/",
                json=data
            )

            if response.status_code == 201:
                result: CreatedInvestorResponse = response.json()

                if 'id' in result:
                    actual_id = result['id']
                else:
                    logger.error("Unexpected response structure for investor '%s': %s",
                                 name, result)
                    return name, None

                logger.debug(
                    "Created investor concurrently: %s -> %s", name, actual_id)
                return name, actual_id

            else:
                logger.error("Failed to create investor '%s': HTTP %d - %s",
                             name, response.status_code, response.text)
                return name, None

        except Exception as e:
            logger.error("Error creating investor '%s': %s", name, e)
            return name, None

    async def _create_investors_individually_fallback(self, investors: Dict) -> Dict[str, str]:
        """
        Create investors individually with proper error handling and logging.
        """
        tasks = [
            self._create_single_investor(name, data) for name, data in investors.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        name_to_id: Dict[str, str] = {}
        success_count = 0

        for result in results:

            if isinstance(result, BaseException):
                logger.error("Concurrent request failed: %s", result)
                continue

            name, investor_id = result
            if investor_id:
                name_to_id[name] = investor_id
                success_count += 1

        logger.info("Concurrent creation summary: %d/%d successful",
                    success_count, len(investors))

        if name_to_id:
            logger.debug("Created investor mappings: %s",
                         {name: id[:8] + "..." for name, id in list(name_to_id.items())[:5]})

        return name_to_id
