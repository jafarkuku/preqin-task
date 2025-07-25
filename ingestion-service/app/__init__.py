"""
Investor management for ingestion service.

Handles creating and fetching investors.
"""

import logging
from typing import Dict, List

import httpx

logger = logging.getLogger(__name__)


class InvestorManager:
    """Manages investor creation and retrieval."""

    def __init__(self, client: httpx.AsyncClient, investor_url: str):
        self.client = client
        self.investor_url = investor_url

    async def bulk_create_investors(self, investors: Dict) -> Dict[str, str]:
        """
        Create investors and return name->ID mapping.

        Args:
            investors: Dictionary of investor data

        Returns:
            Dict mapping investor names to actual service IDs
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

                # Create investors individually to ensure we get proper mapping
                individual_mapping = await self._create_investors_individually(new_investors)
                name_to_id.update(individual_mapping)
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
        Fetch existing investors by name and return name->ID mapping.
        This fixes the duplication issue by properly checking for existing investors.
        """
        name_to_id = {}

        try:
            # Get all investors with pagination to handle large datasets
            page = 1
            all_existing_investors = []

            while True:
                response = await self.client.get(
                    f"{self.investor_url}/api/investors?page={page}&size=100"
                )

                if response.status_code == 200:
                    data = response.json()
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

            # Create name->ID mapping for requested investors
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

    async def _create_investors_individually(self, investors: Dict) -> Dict[str, str]:
        """
        Create investors individually with proper error handling and logging.
        """
        name_to_id = {}

        for name, data in investors.items():
            try:
                # First check if investor already exists (double-check)
                existing_check = await self.client.get(
                    f"{self.investor_url}/api/investors?page=1&size=1000"
                )

                if existing_check.status_code == 200:
                    existing_data = existing_check.json()
                    existing_investors = existing_data.get('investors', [])

                    # Check if this investor already exists
                    existing_investor = next(
                        (inv for inv in existing_investors if inv['name'] == name),
                        None
                    )

                    if existing_investor:
                        name_to_id[name] = existing_investor['id']
                        logger.info(
                            "Found existing investor during individual check: %s", name)
                        continue

                # Create new investor
                logger.debug("Creating investor: %s with data: %s", name, data)

                response = await self.client.post(
                    f"{self.investor_url}/api/investors",
                    json=data
                )

                if response.status_code == 201:
                    result = response.json()
                    actual_id = result['id']
                    name_to_id[name] = actual_id
                    logger.info(
                        "Created investor: '%s' -> ID: %s", name, actual_id)
                else:
                    logger.error("Failed to create investor '%s': HTTP %d - %s",
                                 name, response.status_code, response.text)

            except Exception as e:
                logger.error("Error creating investor '%s': %s", name, e)

        logger.info("Investor creation summary: %d/%d successful",
                    len(name_to_id), len(investors))

        # Debug: Show what we actually created
        if name_to_id:
            logger.debug("Created investor mappings: %s",
                         {name: id[:8] + "..." for name, id in list(name_to_id.items())[:5]})

        return name_to_id
