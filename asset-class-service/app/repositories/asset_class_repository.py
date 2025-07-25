"""
Enhanced Asset Class Repository with bulk operations.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.config import settings
from app.database import get_collection
from app.models.asset_class import (AssetClassCreate, AssetClassResponse,
                                    convert_asset_class_from_db,
                                    prepare_asset_class_for_db)

logger = logging.getLogger(__name__)

MongoDocument = Dict[str, Any]


class AssetClassRepository:
    """
    Repository for asset class database operations with bulk support.
    """

    def __init__(self) -> None:
        self._collection: Optional[AsyncCollection] = None

    @property
    def collection(self) -> AsyncCollection:
        """
        Lazy initialization of collection.
        """
        if self._collection is None:
            self._collection = get_collection(settings.collection_name)
        return self._collection

    async def get_by_ids(self, asset_class_ids: List[str]) -> List[AssetClassResponse]:
        """
        Bulk fetch asset classes by their IDs.=
        """
        if not asset_class_ids:
            return []

        try:
            logger.debug(
                "Bulk fetching %d asset classes from database", len(asset_class_ids))

            cursor = self.collection.find({"id": {"$in": asset_class_ids}})
            docs: List[MongoDocument] = await cursor.to_list(length=len(asset_class_ids))

            asset_classes = [
                converted for doc in docs
                if (converted := convert_asset_class_from_db(doc)) is not None
            ]

            logger.debug("Successfully fetched %d/%d asset classes from database",
                         len(asset_classes), len(asset_class_ids))

            if len(asset_classes) < len(asset_class_ids):
                found_ids = {ac.id for ac in asset_classes}
                missing_ids = set(asset_class_ids) - found_ids
                logger.warning("Asset classes not found: %s",
                               list(missing_ids))

            return asset_classes

        except Exception as e:
            logger.error("Error bulk fetching asset classes: %s", e)
            return []

    async def create(self, asset_class: AssetClassCreate) -> Optional[AssetClassResponse]:
        """
        Create a new asset class in the database.
        """
        asset_class_dict = prepare_asset_class_for_db(asset_class)

        result = await self.collection.insert_one(asset_class_dict)

        created_doc: Optional[MongoDocument] = await self.collection.find_one({
            "_id": result.inserted_id
        })

        if created_doc is None:
            raise RuntimeError("Failed to retrieve created document")

        created_doc.pop("_id", None)

        return convert_asset_class_from_db(created_doc)

    async def get_all(self) -> List[AssetClassResponse]:
        """
        Get all asset classes.
        """
        cursor = self.collection.find().sort("created_at", -1)

        docs: List[MongoDocument] = await cursor.to_list(length=None)

        return [
            converted for doc in docs if (converted := convert_asset_class_from_db(doc)) is not None
        ]

    async def get_by_name(self, name: str) -> Optional[AssetClassResponse]:
        """
        Get an asset class by name (useful for checking duplicates).
        """
        doc: Optional[MongoDocument] = await self.collection.find_one({"name": name})
        if doc:
            return convert_asset_class_from_db(doc)
        return None

    async def count(self, status: Optional[str] = None) -> int:
        """
        Count total asset classes, optionally filtered by status.
        """
        query = {}
        if status:
            query["status"] = status

        return await self.collection.count_documents(query)

    async def bulk_create(self, asset_classes: List[AssetClassCreate]) -> List[AssetClassResponse]:
        """
        Bulk create multiple asset classes efficiently.
        """
        if not asset_classes:
            return []

        try:
            logger.info("Bulk creating %d asset classes", len(asset_classes))

            asset_class_docs = []
            for ac in asset_classes:
                doc = ac.model_dump()
                doc.update({
                    "id": str(uuid4()),
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                asset_class_docs.append(doc)

            result = await self.collection.insert_many(asset_class_docs)

            created_docs = await self.collection.find({
                "_id": {"$in": result.inserted_ids}
            }).to_list(length=len(asset_classes))

            created_asset_classes = []
            for doc in created_docs:
                doc.pop("_id", None)
                created_asset_classes.append(AssetClassResponse(**doc))

            logger.info("Successfully bulk created %d asset classes",
                        len(created_asset_classes))
            return created_asset_classes

        except DuplicateKeyError as e:
            logger.error(
                "Duplicate key error in bulk asset class creation: %s", e)
            return []
        except PyMongoError as e:
            logger.error("Database error bulk creating asset classes: %s", e)
            return []
        except Exception as e:
            logger.error("Unexpected error bulk creating asset classes: %s", e)
            return []


asset_class_repository = AssetClassRepository()
