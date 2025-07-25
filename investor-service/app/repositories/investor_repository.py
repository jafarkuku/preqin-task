"""
Enhanced Investor repository with bulk operations.
"""

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.models.investor import (InvestorCreate, InvestorResponse,
                                 convert_investor_from_db,
                                 prepare_investor_for_db)

logger = logging.getLogger(__name__)


class InvestorRepository:
    """
    Repository for investor database operations with bulk support.

    Handles all database interactions for investor entities.
    """

    def __init__(self, collection: AsyncCollection):
        """
        Initialize the repository with an async collection.

        Args:
            collection: AsyncCollection for investor data
        """
        self.collection = collection

    async def get_by_ids(self, investor_ids: List[str]) -> List[InvestorResponse]:
        """
        Bulk fetch investors by their IDs.

        This is much more efficient than individual queries when you need multiple investors.

        Args:
            investor_ids: List of investor identifiers

        Returns:
            List of found investors (missing IDs are excluded from results)
        """
        if not investor_ids:
            return []

        try:
            logger.debug(
                "Bulk fetching %d investors from database", len(investor_ids))

            # Use MongoDB $in operator for efficient bulk query
            cursor = self.collection.find({"id": {"$in": investor_ids}})
            docs = await cursor.to_list(length=len(investor_ids))

            # Convert to response models
            investors = []
            for doc in docs:
                if converted := convert_investor_from_db(doc):
                    investors.append(converted)

            logger.debug("Successfully fetched %d/%d investors from database",
                         len(investors), len(investor_ids))

            # Log any missing investors for debugging
            if len(investors) < len(investor_ids):
                found_ids = {inv.id for inv in investors}
                missing_ids = set(investor_ids) - found_ids
                logger.warning("Investors not found: %s", list(missing_ids))

            return investors

        except PyMongoError as e:
            logger.error("Database error bulk fetching investors: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error bulk fetching investors: %s", e)
            return []

    async def create_investor(self, investor_data: InvestorCreate) -> Optional[InvestorResponse]:
        """
        Create a new investor.

        Args:
            investor_data: Investor creation data

        Returns:
            InvestorResponse: Created investor or None if failed
        """
        try:
            # Prepare document for database
            db_doc = prepare_investor_for_db(investor_data)

            logger.info("Creating investor: %s", investor_data.name)

            # Insert into database (async operation)
            result = await self.collection.insert_one(db_doc)

            if result.inserted_id:
                # Retrieve the created document
                created_doc = await self.collection.find_one({"id": db_doc["id"]})
                if created_doc:
                    return convert_investor_from_db(created_doc)
                else:
                    logger.error(
                        "Failed to retrieve created investor with id: %s", db_doc["id"])
                    return None

            return None

        except DuplicateKeyError:
            logger.error("Investor with duplicate data already exists")
            return None
        except PyMongoError as e:
            logger.error("Database error creating investor: %s", e)
            return None
        except Exception as e:
            logger.error("Unexpected error creating investor: %s", e)
            return None

    async def bulk_create_investors(self, investors: List[InvestorCreate]) -> List[InvestorResponse]:
        """
        Bulk create multiple investors efficiently.

        Args:
            investors: List of investors to create

        Returns:
            List of created investors
        """
        if not investors:
            return []

        try:
            logger.info("Bulk creating %d investors", len(investors))

            # Prepare all documents for insertion
            investor_docs = [prepare_investor_for_db(inv) for inv in investors]

            # Bulk insert using MongoDB's insert_many
            result = await self.collection.insert_many(investor_docs)

            # Fetch the created documents using the inserted IDs
            created_docs = await self.collection.find({
                "_id": {"$in": result.inserted_ids}
            }).to_list(length=len(investors))

            # Convert to response models
            created_investors = []
            for doc in created_docs:
                if converted := convert_investor_from_db(doc):
                    created_investors.append(converted)

            logger.info("Successfully bulk created %d investors",
                        len(created_investors))
            return created_investors

        except DuplicateKeyError as e:
            logger.error(
                "Duplicate key error in bulk investor creation: %s", e)
            # Could implement partial success handling here
            return []
        except PyMongoError as e:
            logger.error("Database error bulk creating investors: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error bulk creating investors: %s", e)
            return []

    async def get_investor_by_id(self, investor_id: str) -> Optional[InvestorResponse]:
        """
        Get an investor by ID.

        Args:
            investor_id: Unique investor identifier

        Returns:
            InvestorResponse: Found investor or None
        """
        try:
            doc = await self.collection.find_one({"id": investor_id})
            return convert_investor_from_db(doc) if doc else None

        except PyMongoError as e:
            logger.error(
                "Database error retrieving investor %s: %s", investor_id, e)
            return None

    async def _get_total_commitment_amount(self) -> float:
        """
        Get the total commitment amount across all investors in the system.

        This is very efficient since it uses MongoDB's aggregation pipeline
        to sum the total_commitment_amount field across all documents.

        Returns:
            float: Total commitment amount across all investors
        """
        try:
            logger.debug(
                "Calculating total commitment amount across all investors")

            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_commitments": {"$sum": "$total_commitment_amount"}
                    }
                }
            ]

            cursor = await self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)

            if result and len(result) > 0:
                total_commitments = result[0].get("total_commitments", 0.0)
                logger.debug("Total commitment amount: %.2f",
                             total_commitments)
                return float(total_commitments)

            logger.debug("No investors found, returning 0.0")
            return 0.0

        except PyMongoError as e:
            logger.error(
                "Database error calculating total commitment amount: %s", e)
            return 0.0
        except Exception as e:
            logger.error(
                "Unexpected error calculating total commitment amount: %s", e)
            return 0.0

    async def get_all_investors(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get all investors with pagination.

        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: "asc" or "desc"

        Returns:
            Dict with investors list, total count, and pagination info
        """
        try:
            sort_direction = ASCENDING if sort_order.lower() == "asc" else DESCENDING
            sort_criteria = [(sort_by, sort_direction)]

            logger.info(
                "Getting all investors, skip: %d, limit: %d", skip, limit)

            tasks = [
                self.collection.count_documents({}),
                self._get_total_commitment_amount()]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_count: int = 0
            total_commitment_amount: float = 0.0

            if isinstance(results[0], Exception):
                logger.error("Error getting total count: %s", results[0])
                total_count = 0
            elif isinstance(results[0], int):
                total_count = results[0]
            else:
                logger.warning(
                    "Unexpected type for total_count: %s, defaulting to 0", type(results[0]))
                total_count = 0

            if isinstance(results[1], Exception):
                logger.error(
                    "Error getting total commitment amount: %s", results[1])
                total_commitment_amount = 0.0
            elif isinstance(results[1], (int, float)):
                total_commitment_amount = float(
                    results[1])
            else:
                logger.warning(
                    "Unexpected type for total_commitment_amount: %s, defaulting to 0.0", type(results[1]))
                total_commitment_amount = 0.0

            # Get investors with pagination
            cursor = self.collection.find({}).sort(
                sort_criteria).skip(skip).limit(limit)

            # Convert to response models
            investors = [
                convert_investor_from_db(doc)
                async for doc in cursor
            ]

            total_pages = (total_count + limit - 1) // limit
            current_page = (skip // limit) + 1

            return {
                "investors": investors,
                "total": total_count,
                "total_commitment_amount": total_commitment_amount,
                "page": current_page,
                "size": limit,
                "total_pages": total_pages,
                "has_next": skip + limit < total_count,
                "has_prev": skip > 0
            }

        except PyMongoError as e:
            logger.error("Database error querying investors: %s", e)
            return {
                "investors": [],
                "total": 0,
                "page": 1,
                "size": limit,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }

    async def update_commitment_metrics(self, investor_id: str, commitment_count: int, total_amount: Decimal) -> bool:
        """
        Update investor's commitment metrics (called by event handlers).

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.debug("Updating commitment metrics for investor %s: count=%d, amount=%.2f",
                         investor_id, commitment_count, float(total_amount))

            result = await self.collection.update_one(
                {"id": investor_id},
                {
                    "$set": {
                        "commitment_count": commitment_count,
                        "total_commitment_amount": float(total_amount),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )

            success = result.modified_count > 0
            if success:
                logger.debug(
                    "Successfully updated commitment metrics for investor %s", investor_id)
            else:
                logger.warning(
                    "No investor found to update metrics for ID: %s", investor_id)

            return success

        except PyMongoError as e:
            logger.error("Database error updating commitment metrics for investor %s: %s",
                         investor_id, e)
            return False
        except Exception as e:
            logger.error("Unexpected error updating commitment metrics for investor %s: %s",
                         investor_id, e)
            return False

    async def bulk_create(self, investors: List[InvestorCreate]) -> List[InvestorResponse]:
        """
        Bulk create multiple investors.

        Args:
            investors: List of investors to create

        Returns:
            List of created investors
        """
        if not investors:
            return []

        try:
            logger.debug("Bulk creating %d investors", len(investors))

            investor_dicts = [prepare_investor_for_db(
                inv) for inv in investors]

            result = await self.collection.insert_many(investor_dicts)

            created_docs = await self.collection.find({
                "_id": {"$in": result.inserted_ids}
            }).to_list(length=len(investors))

            created_investors = []
            for doc in created_docs:
                if converted := convert_investor_from_db(doc):
                    created_investors.append(converted)

            logger.debug("Successfully bulk created %d investors",
                         len(created_investors))
            return created_investors

        except PyMongoError as e:
            logger.error("Database error bulk creating investors: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error bulk creating investors: %s", e)
            return []
