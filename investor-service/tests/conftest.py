from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.factories.investor import (InvestorCreateFactory,
                                      InvestorResponseFactory,
                                      MongoInvestorFactory)


@pytest.fixture
def mock_mongo_collection():
    """mocked MongoDB AsyncCollection for use with pymongo"""
    mock_collection = MagicMock()

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock()
    mock_collection.find.return_value = mock_cursor

    mock_collection.insert_one = AsyncMock()
    mock_collection.find_one = AsyncMock()
    mock_collection.insert_many = AsyncMock()
    mock_collection.count_documents = AsyncMock()
    mock_collection.update_one = AsyncMock()

    return mock_collection


@pytest.fixture
def investor_repository(mock_mongo_collection):
    """Create repository with mocked collection."""
    from app.repositories.investor_repository import InvestorRepository
    return InvestorRepository(mock_mongo_collection)


@pytest.fixture
def sample_investor_create():
    """Sample InvestorCreate model."""
    return InvestorCreateFactory()


@pytest.fixture
def sample_investor_response():
    """Sample InvestorResponse model."""
    return InvestorResponseFactory()


@pytest.fixture
def sample_mongo_docs():
    """Sample MongoDB documents."""
    return MongoInvestorFactory.build_batch(2)


@pytest.fixture
def mock_event_subscriber():
    """Mock event subscriber."""
    subscriber = AsyncMock()
    subscriber.connect = AsyncMock()
    subscriber.disconnect = AsyncMock()
    subscriber.start_listening = AsyncMock()
    return subscriber
