import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.asset_class import AssetClassCreate, AssetClassResponse


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_asset_class_create():
    """Sample AssetClassCreate model for testing."""
    return AssetClassCreate(
        name="Test Private Equity",
        description="Test private equity investments",
        status="active"
    )


@pytest.fixture
def sample_asset_class_response():
    """Sample AssetClassResponse model for testing."""
    return AssetClassResponse(
        id="test-id-123",
        name="Test Private Equity",
        description="Test private equity investments",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_asset_classes_list():
    """List of sample asset classes for bulk testing."""
    return [
        AssetClassCreate(name="Private Equity",
                         description="PE investments", status="active"),
        AssetClassCreate(name="Real Estate",
                         description="RE investments", status="active"),
        AssetClassCreate(name="Infrastructure",
                         description="Infrastructure investments", status="inactive")
    ]


@pytest.fixture
def mock_mongo_collection():
    """Properly mocked MongoDB AsyncCollection for use with pymongo[asyncio]."""
    mock_collection = MagicMock()

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find.return_value = mock_cursor

    mock_collection.insert_one = AsyncMock()
    mock_collection.find_one = AsyncMock()
    mock_collection.insert_many = AsyncMock()
    mock_collection.count_documents = AsyncMock()

    return mock_collection


@pytest.fixture
def asset_class_repository(mock_mongo_collection):
    """Repository with mocked MongoDB collection."""
    from app.repositories.asset_class_repository import AssetClassRepository
    repo = AssetClassRepository()
    repo._collection = mock_mongo_collection
    return repo


@pytest.fixture
def sample_mongo_docs():
    """Sample MongoDB documents for testing."""
    return [
        {
            "_id": "mongo_id_1",
            "id": "test-id-1",
            "name": "Private Equity",
            "description": "PE investments",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "mongo_id_2",
            "id": "test-id-2",
            "name": "Real Estate",
            "description": "RE investments",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
