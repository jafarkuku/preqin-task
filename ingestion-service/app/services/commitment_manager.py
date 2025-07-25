"""
Commitment management for ingestion service.

Handles creating commitments and managing duplicates.
"""

import logging
from typing import Dict, List, TypedDict

import httpx

logger = logging.getLogger(__name__)


class CommitmentData(TypedDict):
    """Shape of commitment data from CSV parser."""
    investor_name: str
    asset_class_name: str
    amount: float
    currency: str


class CommitmentCreateRequest(TypedDict):
    """Data sent to commitment service for creation."""
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str


class CreatedCommitmentResponse(TypedDict):
    """Response from commitment service when creating a commitment."""
    id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str
    created_at: str
    updated_at: str


class CommitmentListResponse(TypedDict):
    """Response from commitment service list endpoint."""
    commitments: List[CreatedCommitmentResponse]
    total: int
    total_amount: float
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CommitmentManager:
    """Manages commitment creation and deduplication."""

    def __init__(self, client: httpx.AsyncClient, commitment_url: str):
        self.client = client
        self.commitment_url = commitment_url

    async def bulk_create_commitments(
        self,
        commitments_data: List[CommitmentData],
        investor_name_to_id: Dict[str, str],
        asset_class_name_to_id: Dict[str, str]
    ) -> int:
        """
        Create ALL commitments.
        """
        logger.info("Starting concurrent commitment creation process")

        if investor_name_to_id:
            sample_investors = list(investor_name_to_id.keys())[:3]
            logger.info("📋 Sample investor names in mapping: %s",
                        sample_investors)

        if asset_class_name_to_id:
            sample_asset_classes = list(asset_class_name_to_id.keys())[:3]
            logger.info("📋 Sample asset class names in mapping: %s",
                        sample_asset_classes)

        existing_commitments = await self._fetch_existing_commitments()

        bulk_commitments: list[CommitmentCreateRequest] = []

        for commitment in commitments_data:
            investor_name = commitment['investor_name']
            asset_class_name = commitment['asset_class_name']

            investor_id = investor_name_to_id.get(investor_name)
            asset_class_id = asset_class_name_to_id.get(asset_class_name)

            if not investor_id or not asset_class_id:
                continue

            unique_commitment_key = f"{investor_id}:{asset_class_id}:{commitment['amount']}:{commitment['currency']}"

            if unique_commitment_key in existing_commitments:
                continue

            bulk_commitments.append({
                'investor_id': investor_id,
                'asset_class_id': asset_class_id,
                'amount': float(commitment['amount']),
                'currency': commitment['currency']
            })

        if not bulk_commitments:
            logger.warning("No valid commitments to create!")
            return 0

        logger.info("Creating %d commitments in bulk...",
                    len(bulk_commitments))

        try:
            response = await self.client.post(f"{self.commitment_url}/api/commitments/bulk-create", json=bulk_commitments)

            if response.status_code == 200:
                created = response.json()
                logger.info(
                    "Successfully bulk created %d commitments", len(created))
                return len(created)
            else:
                logger.error("Bulk create failed: HTTP %d - %s",
                             response.status_code, response.text)
                return 0
        except Exception as e:
            logger.error(
                "Fatal error in concurrent commitment creation: %s", e)
            return 0

    async def _fetch_existing_commitments(self) -> set:
        """
        Fetch existing commitments and return a set of unique keys to avoid duplicates.
        """
        existing_keys: set[str] = set()

        try:
            page = 1
            while True:
                url = f"{self.commitment_url}/api/commitments/?page={page}&size=100"

                response: httpx.Response | None = None

                try:
                    response = await self.client.get(url)
                    if response.status_code == 200:
                        break
                except Exception:
                    continue

                if not response or response.status_code != 200:
                    logger.warning(
                        "Failed to fetch existing commitments on page %d", page)
                    break

                data: CommitmentListResponse = response.json()
                commitments = data.get('commitments', [])

                if not commitments:
                    break

                for commitment in commitments:
                    key = f"{commitment['investor_id']}:{commitment['asset_class_id']}:{commitment['amount']}:{commitment['currency']}"
                    existing_keys.add(key)

                if not data.get('has_next', False):
                    break
                page += 1

            logger.info(
                "Found %d existing commitments to avoid duplicates", len(existing_keys))

        except Exception as e:
            logger.error("Error fetching existing commitments: %s", e)

        return existing_keys
