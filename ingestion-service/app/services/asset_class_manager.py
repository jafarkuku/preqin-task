"""
Asset class management for ingestion service.

Handles creating and fetching asset classes.
"""

import asyncio
import logging
from typing import Dict, List, TypedDict

import httpx

logger = logging.getLogger(__name__)


class AssetClassData(TypedDict):
    """Shape of asset class data passed to bulk_create_asset_classes."""
    name: str
    description: str
    status: str


class AssetClassListResponse(TypedDict):
    """Response from asset class service list endpoint."""
    id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str


class AssetClassCreateResponse(TypedDict):
    """Response from individual asset class create endpoint."""
    data: AssetClassListResponse


class AssetClassManager:
    """Manages asset class creation and retrieval."""

    def __init__(self, client: httpx.AsyncClient, asset_class_url: str) -> None:
        self.client = client
        self.asset_class_url = asset_class_url

    async def bulk_create_asset_classes(self, asset_classes: Dict[str, AssetClassData]) -> Dict[str, str]:
        """
        Create asset classes and return name to ID mapping.
        """
        if not asset_classes:
            return {}

        logger.info(
            "Processing %d asset classes (create or fetch existing)", len(asset_classes))

        try:
            name_to_id = await self._fetch_existing_asset_classes(list(asset_classes.keys()))

            new_asset_classes = {
                name: data for name, data in asset_classes.items()
                if name not in name_to_id
            }

            if new_asset_classes:
                logger.info("Creating %d new asset classes (found %d existing)",
                            len(new_asset_classes), len(name_to_id))

                bulk_mapping = await self._bulk_create_asset_classes(new_asset_classes)
                name_to_id.update(bulk_mapping)
            else:
                logger.info(
                    "All %d asset classes already exist, no creation needed", len(asset_classes))

            logger.info("Final asset class mapping: %d total", len(name_to_id))
            return name_to_id

        except Exception as e:
            logger.error("Error in asset class processing: %s", e)
            return {}

    async def _fetch_existing_asset_classes(self, asset_class_names: List[str]) -> Dict[str, str]:
        """
        Fetch existing asset classes by name and return name->ID mapping.
        """
        name_to_id: Dict[str, str] = {}

        try:
            response = await self.client.get(
                f"{self.asset_class_url}/api/asset-classes/")

            asset_classes: List[AssetClassListResponse] = response.json()

            if not asset_classes:
                logger.warning("No asset classes found in the system")
                return name_to_id

            for asset_class in asset_classes:
                if asset_class['name'] in asset_class_names:
                    name_to_id[asset_class['name']] = asset_class['id']
                    logger.debug("Found existing asset class: %s -> %s",
                                 asset_class['name'], asset_class['id'])

            logger.info("Found %d existing asset classes out of %d requested",
                        len(name_to_id), len(asset_class_names))

        except Exception as e:
            logger.error("Error fetching existing asset classes: %s", e)

        return name_to_id

    async def _bulk_create_asset_classes(self, asset_classes: Dict[str, AssetClassData]) -> Dict[str, str]:
        """
        Create asset classes using the bulk endpoint for maximum efficiency.
        """
        if not asset_classes:
            return {}

        name_to_id: Dict[str, str] = {}

        try:
            asset_classes_list: List[AssetClassData] = []
            name_order: List[str] = []

            for name, data in asset_classes.items():
                asset_classes_list.append(data)
                name_order.append(name)

            logger.info("Bulk creating %d asset classes in single request", len(
                asset_classes_list))

            response = await self.client.post(
                f"{self.asset_class_url}/api/asset-classes/bulk-create",
                json=asset_classes_list
            )

            if response.status_code == 200:
                created_asset_classes: List[AssetClassListResponse] = response.json(
                )

                if isinstance(created_asset_classes, list):
                    for i, created_asset_class in enumerate(created_asset_classes):
                        if i < len(name_order):
                            name = name_order[i]
                            asset_class_id = created_asset_class.get('id')
                            if asset_class_id:
                                name_to_id[name] = asset_class_id
                                logger.debug("Bulk created asset class: %s -> %s",
                                             name, asset_class_id)

                logger.info("Successfully bulk created %d/%d asset classes",
                            len(name_to_id), len(asset_classes))

            else:
                logger.error("Bulk create failed: HTTP %d - %s",
                             response.status_code, response.text)

                logger.warning("Falling back to individual creates...")
                name_to_id = await self._create_asset_classes_individually_fallback(asset_classes)

        except Exception as e:
            logger.error("Error in bulk create: %s", e)

            logger.warning(
                "Falling back to individual creates due to error...")
            name_to_id = await self._create_asset_classes_individually_fallback(asset_classes)

        return name_to_id

    async def _create_single_asset_class(self, name: str, data: AssetClassData) -> tuple[str, str | None]:
        """Create a single asset class and return (name, id) tuple."""
        try:
            logger.debug("Creating asset class concurrently: %s", name)

            response = await self.client.post(
                f"{self.asset_class_url}/api/asset-classes",
                json=data
            )

            if response.status_code == 201:
                result: AssetClassCreateResponse = response.json()
                if 'data' in result and 'id' in result['data']:
                    actual_id = result['data']['id']
                elif 'id' in result:
                    actual_id = result['id']
                else:
                    logger.error("Unexpected response structure for asset class '%s': %s",
                                 name, result)
                    return name, None

                logger.debug(
                    "Created asset class concurrently: %s -> %s", name, actual_id)
                return name, actual_id

            else:
                logger.error("Failed to create asset class '%s': HTTP %d - %s",
                             name, response.status_code, response.text)
                return name, None

        except Exception as e:
            logger.error("Error creating asset class '%s': %s", name, e)
            return name, None

    async def _create_asset_classes_individually_fallback(self, asset_classes: Dict[str, AssetClassData]) -> Dict[str, str]:
        """
        Create asset classes individually with proper error handling.
        """

        tasks = [
            self._create_single_asset_class(name, data) for name, data in asset_classes.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        name_to_id: Dict[str, str] = {}
        success_count = 0

        for result in results:
            if isinstance(result, BaseException):
                logger.error("Concurrent request failed: %s", result)
                continue

            name, asset_id = result
            if asset_id:
                name_to_id[name] = asset_id
                success_count += 1

        logger.info("Concurrent creation summary: %d/%d successful",
                    success_count, len(asset_classes))

        if name_to_id:
            logger.debug("Created asset class mappings: %s",
                         {name: id[:8] + "..." for name, id in list(name_to_id.items())[:5]})

        return name_to_id
