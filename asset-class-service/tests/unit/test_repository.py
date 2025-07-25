from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.models.asset_class import AssetClassResponse


class TestAssetClassRepository:
    """Test cases for AssetClassRepository."""

    @pytest.mark.asyncio
    async def test_create_asset_class_success(self, asset_class_repository, sample_asset_class_create, mock_mongo_collection):
        """Test successful asset class creation."""

        inserted_id = "mock_inserted_id"
        created_doc = {
            "_id": inserted_id,
            "id": "test-id-123",
            "name": sample_asset_class_create.name,
            "description": sample_asset_class_create.description,
            "status": sample_asset_class_create.status,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        mock_mongo_collection.insert_one.return_value = MagicMock(
            inserted_id=inserted_id)
        mock_mongo_collection.find_one.return_value = created_doc

        # Mock the prepare function
        with patch('app.repositories.asset_class_repository.prepare_asset_class_for_db') as mock_prepare:
            mock_prepare.return_value = created_doc

            result = await asset_class_repository.create(sample_asset_class_create)

            assert result is not None
            assert result.name == sample_asset_class_create.name
            assert result.description == sample_asset_class_create.description
            assert result.status == sample_asset_class_create.status
            mock_mongo_collection.insert_one.assert_called_once()
            mock_mongo_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_asset_class_retrieve_failure(self, asset_class_repository, sample_asset_class_create, mock_mongo_collection):
        """Test creation failure when document can't be retrieved."""

        mock_mongo_collection.insert_one.return_value = MagicMock(
            inserted_id="test_id")
        mock_mongo_collection.find_one.return_value = None

        with patch('app.repositories.asset_class_repository.prepare_asset_class_for_db') as mock_prepare:
            mock_prepare.return_value = {"test": "doc"}

            with pytest.raises(RuntimeError, match="Failed to retrieve created document"):
                await asset_class_repository.create(sample_asset_class_create)

    @pytest.mark.asyncio
    async def test_get_by_ids_success(self, asset_class_repository, mock_mongo_collection, sample_mongo_docs):
        """Test successful bulk fetch by IDs."""
        asset_class_ids = ["test-id-1", "test-id-2"]

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_mongo_docs)
        mock_mongo_collection.find.return_value = mock_cursor

        with patch('app.models.asset_class.convert_asset_class_from_db') as mock_convert:
            mock_convert.side_effect = [
                AssetClassResponse(**{k: v for k, v in doc.items() if k != "_id"}) for doc in sample_mongo_docs
            ]

            result = await asset_class_repository.get_by_ids(asset_class_ids)

            assert len(result) == 2
            assert result[0].name == "Private Equity"
            assert result[1].name == "Real Estate"
            assert all(isinstance(r, AssetClassResponse) for r in result)
            mock_mongo_collection.find.assert_called_once_with(
                {"id": {"$in": asset_class_ids}})

    @pytest.mark.asyncio
    async def test_get_by_ids_database_error(self, asset_class_repository, mock_mongo_collection):
        """Test bulk fetch with database error."""

        mock_mongo_collection.find.side_effect = PyMongoError("Database error")

        result = await asset_class_repository.get_by_ids(["test-id"])

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_name_found(self, asset_class_repository, mock_mongo_collection, sample_mongo_docs):
        """Test finding asset class by name."""

        mock_mongo_collection.find_one.return_value = sample_mongo_docs[0]

        with patch('app.repositories.asset_class_repository.convert_asset_class_from_db') as mock_convert:
            mock_convert.return_value = AssetClassResponse(
                id="test-id-1", name="Private Equity", description="PE investments",
                status="active", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            )

            result = await asset_class_repository.get_by_name("Private Equity")

            assert result is not None
            assert result.name == "Private Equity"
            mock_mongo_collection.find_one.assert_called_once_with(
                {"name": "Private Equity"})

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, asset_class_repository, mock_mongo_collection):
        """Test asset class not found by name."""
        mock_mongo_collection.find_one.return_value = None

        result = await asset_class_repository.get_by_name("Non-existent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, asset_class_repository, mock_mongo_collection, sample_mongo_docs):
        """Test get_all with pagination parameters."""
        mock_cursor = MagicMock()

        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)

        async def mock_to_list(length=None):
            return sample_mongo_docs

        mock_cursor.to_list = mock_to_list
        mock_mongo_collection.find.return_value = mock_cursor

        with patch('app.repositories.asset_class_repository.convert_asset_class_from_db') as mock_convert:
            mock_convert.side_effect = [
                AssetClassResponse(
                    id="test-id-1", name="Private Equity", description="PE",
                    status="active", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                ),
                AssetClassResponse(
                    id="test-id-2", name="Real Estate", description="RE",
                    status="active", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                )
            ]

            result = await asset_class_repository.get_all(skip=10, limit=5, status="active")

            assert len(result) == 2
            mock_mongo_collection.find.assert_called_once_with(
                {"status": "active"})
            mock_cursor.skip.assert_called_once_with(10)
            mock_cursor.limit.assert_called_once_with(5)
            mock_cursor.sort.assert_called_once_with("created_at", -1)

    @pytest.mark.asyncio
    async def test_count_total(self, asset_class_repository, mock_mongo_collection):
        """Test counting all asset classes."""

        mock_mongo_collection.count_documents.return_value = 42

        result = await asset_class_repository.count()

        assert result == 42
        mock_mongo_collection.count_documents.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_count_with_status_filter(self, asset_class_repository, mock_mongo_collection):
        """Test counting with status filter."""

        mock_mongo_collection.count_documents.return_value = 15

        result = await asset_class_repository.count(status="active")

        assert result == 15
        mock_mongo_collection.count_documents.assert_called_once_with(
            {"status": "active"})

    @pytest.mark.asyncio
    async def test_bulk_create_success(self, asset_class_repository, mock_mongo_collection, sample_asset_classes_list):
        """Test successful bulk creation."""

        inserted_ids = ["id1", "id2", "id3"]
        created_docs = [
            {"_id": "id1", "id": "uuid1", "name": "Private Equity", "status": "active", "description": "PE investments",
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"_id": "id2", "id": "uuid2", "name": "Real Estate", "status": "active", "description": "RE investments",
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"_id": "id3", "id": "uuid3", "name": "Infrastructure", "status": "inactive", "description": "Infrastructure investments",
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
        ]

        mock_mongo_collection.insert_many.return_value = MagicMock(
            inserted_ids=inserted_ids)

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=created_docs)
        mock_mongo_collection.find.return_value = mock_cursor

        result = await asset_class_repository.bulk_create(sample_asset_classes_list)

        assert len(result) == 3
        assert all(isinstance(ac, AssetClassResponse) for ac in result)
        assert result[0].name == "Private Equity"
        assert result[1].name == "Real Estate"
        assert result[2].name == "Infrastructure"
        mock_mongo_collection.insert_many.assert_called_once()
        mock_mongo_collection.find.assert_called_once_with(
            {"_id": {"$in": inserted_ids}}
        )

    @pytest.mark.asyncio
    async def test_bulk_create_empty_list(self, asset_class_repository):
        """Test bulk create with empty list."""

        result = await asset_class_repository.bulk_create([])

        assert result == []

    @pytest.mark.asyncio
    async def test_bulk_create_duplicate_key_error(self, asset_class_repository, mock_mongo_collection, sample_asset_classes_list):
        """Test bulk create with duplicate key error."""

        mock_mongo_collection.insert_many.side_effect = DuplicateKeyError(
            "Duplicate key")

        result = await asset_class_repository.bulk_create(sample_asset_classes_list)

        assert result == []

    @pytest.mark.asyncio
    async def test_bulk_create_pymongo_error(self, asset_class_repository, mock_mongo_collection, sample_asset_classes_list):
        """Test bulk create with general PyMongo error."""

        mock_mongo_collection.insert_many.side_effect = PyMongoError(
            "Database error")

        result = await asset_class_repository.bulk_create(sample_asset_classes_list)

        assert result == []
