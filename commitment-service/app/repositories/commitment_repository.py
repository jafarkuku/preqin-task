"""
Commitment repository for database operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, List, Optional, Tuple, TypedDict

import aiosqlite

from app.models.commitment import (AssetBreakdown, CommitmentCreate,
                                   CommitmentResponse,
                                   convert_commitment_from_db,
                                   prepare_commitment_for_db)
from app.services import event_publisher

logger = logging.getLogger(__name__)


class CommitmentFilters(TypedDict, total=False):
    investor_id: str | None
    asset_class_id: str | None
    currency: str | None


class PaginationInfo(TypedDict):
    """Pagination information"""
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CommitmentDbDict(TypedDict):
    """Type definition for commitment database dictionary."""
    id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str
    created_at: datetime
    updated_at: datetime


class CommitmentEventData(TypedDict):
    """Type definition for commitment event data."""
    id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str


class CommitmentListResult(PaginationInfo):
    """Type definition for paginated commitment list results."""
    commitments: List[CommitmentResponse]
    asset_breakdowns: List[AssetBreakdown]
    total: int
    total_amount: float


class CommitmentRepository:
    """
    Repository for commitment database operations.
    """

    def __init__(self, connection: aiosqlite.Connection):
        """
        Initialize the repository with a database connection.
        """
        self.connection = connection

    def __build_where_clause(self, filters: CommitmentFilters) -> tuple[str, list[Any]]:
        """
        Builds a SQL WHERE clause and parameter list from a dict of filters.
        """
        conditions = []
        params = []

        for field, value in filters.items():
            if value is not None:
                conditions.append(f"{field} = ?")
                params.append(value)

        clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return clause, params

    def __get_pagination_info(self, skip, limit, total) -> PaginationInfo:
        """Gets the pagination data"""
        return {
            "page": (skip // limit) + 1,
            "size": limit,
            "total_pages": (total + limit - 1) // limit,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }

    async def create_commitment(self, commitment_data: CommitmentCreate) -> Optional[CommitmentResponse]:
        """
        Create a new commitment.
        """
        try:
            db_doc = prepare_commitment_for_db(commitment_data)

            logger.info("Creating commitment for investor: %s",
                        commitment_data.investor_id)

            await self.connection.execute("""
                INSERT INTO commitments (id, investor_id, asset_class_id, amount, currency, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                db_doc["id"],
                db_doc["investor_id"],
                db_doc["asset_class_id"],
                db_doc["amount"],
                db_doc["currency"],
                db_doc["created_at"],
                db_doc["updated_at"]
            ))

            await self.connection.commit()

            created_commitment = await self.get_commitment_by_id(db_doc["id"])

            if created_commitment:
                logger.info(
                    "Successfully created commitment with ID: %s", db_doc["id"])

                await event_publisher.publish_commitment_created({
                    "id": created_commitment.id,
                    "investor_id": created_commitment.investor_id,
                    "asset_class_id": created_commitment.asset_class_id,
                    "amount": created_commitment.amount,
                    "currency": created_commitment.currency
                })

                return created_commitment
            else:
                logger.error(
                    "Failed to retrieve created commitment with id: %s", db_doc["id"])
                return None

        except Exception as e:
            logger.error("Error creating commitment: %s", e)
            await self.connection.rollback()
            return None

    CommitmentDbRow = Tuple[str, str, str, float, str, datetime, datetime]

    async def bulk_create_commitments(self, commitments: List[CommitmentCreate]) -> List[CommitmentResponse]:
        """
        Bulk create multiple commitments efficiently.

        Args:
            commitments: List of commitments to create

        Returns:
            List of created commitments
        """
        if not commitments:
            return []

        try:
            logger.info("Bulk creating %d commitments", len(commitments))

            # Prepare all documents for insertion
            commitment_docs = []
            commitment_ids = []

            for commitment in commitments:
                db_doc = prepare_commitment_for_db(commitment)
                commitment_ids.append(db_doc["id"])
                commitment_docs.append((
                    db_doc["id"],
                    db_doc["investor_id"],
                    db_doc["asset_class_id"],
                    db_doc["amount"],
                    db_doc["currency"],
                    db_doc["created_at"],
                    db_doc["updated_at"]
                ))

            # Bulk insert using executemany
            await self.connection.executemany("""
                INSERT INTO commitments (id, investor_id, asset_class_id, amount, currency, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, commitment_docs)

            await self.connection.commit()

            # Fetch all created commitments in one query
            placeholders = ','.join('?' for _ in commitment_ids)
            cursor = await self.connection.execute(f"""
                SELECT id, investor_id, asset_class_id, amount, currency, created_at, updated_at
                FROM commitments
                WHERE id IN ({placeholders})
            """, commitment_ids)

            rows = await cursor.fetchall()

            created_commitments = []
            for row in rows:
                row_dict = {
                    "id": row[0],
                    "investor_id": row[1],
                    "asset_class_id": row[2],
                    "amount": row[3],
                    "currency": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }

                commitment_response = convert_commitment_from_db(row_dict)
                if commitment_response:
                    created_commitments.append(commitment_response)

            logger.info("Successfully bulk created %d commitments",
                        len(created_commitments))

            publish_tasks = [
                event_publisher.publish_commitment_created({
                    "id": commitment.id,
                    "investor_id": commitment.investor_id,
                    "asset_class_id": commitment.asset_class_id,
                    "amount": commitment.amount,
                    "currency": commitment.currency
                }) for commitment in created_commitments
            ]

            results = await asyncio.gather(*publish_tasks, return_exceptions=True)

            for result in results:
                if isinstance(results, BaseException):
                    logger.error("Concurrent task failed for commitment publish: %s",
                                 result)

            return created_commitments

        except Exception as e:
            logger.error("Error bulk creating commitments: %s", e)
            await self.connection.rollback()
            return []

    async def get_commitment_by_id(self, commitment_id: str) -> Optional[CommitmentResponse]:
        """
        Get a commitment by ID.
        """
        try:
            cursor = await self.connection.execute("""
                SELECT id, investor_id, asset_class_id, amount, currency, created_at, updated_at
                FROM commitments
                WHERE id = ?
            """, (commitment_id,))

            row = await cursor.fetchone()

            if row:
                # Convert row to dict
                columns = [description[0]
                           for description in cursor.description]
                row_dict = dict(zip(columns, row))
                return convert_commitment_from_db(row_dict)

            return None

        except Exception as e:
            logger.error(
                "Database error retrieving commitment %s: %s", commitment_id, e)
            return None

    async def get_commitments(
        self,
        skip: int = 0,
        limit: int = 100,
        investor_id: Optional[str] = None,
        asset_class_id: Optional[str] = None,
        currency: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> CommitmentListResult:
        """
        Fetch commitments with optional filters, pagination, and asset breakdowns.
        """
        try:
            valid_sort_fields = {
                "id", "investor_id", "asset_class_id", "amount", "currency", "created_at", "updated_at"
            }
            sort_by = sort_by if sort_by in valid_sort_fields else "created_at"
            sort_dir = "DESC" if sort_order.lower() == "desc" else "ASC"

            filters: CommitmentFilters = {
                "investor_id": investor_id,
                "asset_class_id": asset_class_id or None,
                "currency": currency or None
            }
            where_clause, params = self.__build_where_clause(filters)

            asset_class_breakdown_filters: CommitmentFilters = {
                "investor_id": investor_id,
                "asset_class_id": None,
                "currency": currency or None
            }
            asset_class_breakdown_where_clause, asset_class_breakdown_params = self.__build_where_clause(
                asset_class_breakdown_filters)

            count_sql = f"SELECT COUNT(*) FROM commitments {where_clause}"
            count_cursor = await self.connection.execute(count_sql, params)
            count_row = await count_cursor.fetchone()
            total_count = count_row[0] if count_row else 0

            total_sql = f"SELECT SUM(amount) FROM commitments {asset_class_breakdown_where_clause}"
            total_cursor = await self.connection.execute(total_sql, asset_class_breakdown_params)
            total_row = await total_cursor.fetchone()
            total_amount = float(
                total_row[0]) if total_row and total_row[0] else 0.0

            asset_class_breakdown_sql = f"""
                SELECT asset_class_id, SUM(amount), COUNT(*)
                FROM commitments
                {asset_class_breakdown_where_clause}
                GROUP BY asset_class_id
                ORDER BY SUM(amount) DESC
            """
            breakdown_cursor = await self.connection.execute(asset_class_breakdown_sql, asset_class_breakdown_params)
            breakdown_rows = await breakdown_cursor.fetchall()

            asset_breakdowns: List[AssetBreakdown] = []
            for asset_class_id_val, asset_total, count in breakdown_rows:
                if asset_class_id_val is None:
                    continue

                percentage = (asset_total / total_amount *
                              100) if total_amount > 0 else 0.0
                asset_breakdowns.append(
                    AssetBreakdown(
                        asset_class_id=asset_class_id_val,
                        total_amount=float(asset_total),
                        commitment_count=int(count),
                        percentage_of_total=round(percentage, 2)
                    )
                )

            main_sql = f"""
                SELECT id, investor_id, asset_class_id, amount, currency, created_at, updated_at
                FROM commitments
                {where_clause}
                ORDER BY {sort_by} {sort_dir}
                LIMIT ? OFFSET ?
            """
            cursor = await self.connection.execute(main_sql, list(params) + [limit, skip])
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            commitments = [
                commitment for commitment in (
                    convert_commitment_from_db(dict(zip(columns, row))) for row in rows
                ) if commitment
            ]

            return CommitmentListResult({
                "commitments": commitments,
                "asset_breakdowns": asset_breakdowns,  # Always ALL assets
                "total": total_count,  # Count of filtered commitments
                "total_amount": total_amount,  # Grand total for context
                **self.__get_pagination_info(skip, limit, total_count)
            })

        except Exception as e:
            logger.error("Database error querying commitments: %s", e)
            return CommitmentListResult({
                "commitments": [],
                "asset_breakdowns": [],
                "total": 0,
                "total_amount": 0.0,
                **self.__get_pagination_info(skip, limit, 0)
            })
