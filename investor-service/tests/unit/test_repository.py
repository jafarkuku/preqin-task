from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from pymongo.errors import DuplicateKeyError

from app.models.investor import InvestorResponse
from tests.factories.investor import (InvestorCreateFactory,
                                      MongoInvestorFactory)


class TestInvestorRepository:
    """Test cases for InvestorRepository."""

    @pytest.mark.asyncio
    async def test_create_investor_success(self, investor_repository, sample_investor_create, mock_mongo_collection):
        """Test successful investor creation."""
        created_doc = {
            "id": "test-inv-123",
            "name": sample_investor_create.name,
            "investor_type": sample_investor_create.investor_type,
            "country": sample_investor_create.country,
            "date_added": sample_investor_create.date_added,
            "commitment_count": 0,
            "total_commitment_amount": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        mock_mongo_collection.insert_one.return_value = MagicMock(
            inserted_id="test_id")
        mock_mongo_collection.find_one.return_value = created_doc

        result = await investor_repository.create_investor(sample_investor_create)

        assert result is not None
        assert result.name == sample_investor_create.name
        assert result.investor_type == sample_investor_create.investor_type
        assert result.commitment_count == 0
        assert result.total_commitment_amount == 0.0
        mock_mongo_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_investor_duplicate_error(self, investor_repository, sample_investor_create, mock_mongo_collection):
        """Test investor creation with duplicate key error."""
        mock_mongo_collection.insert_one.side_effect = DuplicateKeyError(
            "Duplicate key")

        result = await investor_repository.create_investor(sample_investor_create)

        assert result is None

    @pytest.mark.asyncio
    async def test_bulk_create_investors_success(self, investor_repository, mock_mongo_collection):
        """Test successful bulk investor creation using factories."""

        investor_inputs = InvestorCreateFactory.build_batch(2)

        inserted_ids = ["id1", "id2"]

        created_docs = [
            MongoInvestorFactory(
                id=f"inv-{i + 1}",
                name=inv.name,
                investor_type=inv.investor_type,
                country=inv.country,
                date_added=inv.date_added,
                commitment_count=0,
                total_commitment_amount=0.0,
            )
            for i, inv in enumerate(investor_inputs)
        ]

        mock_mongo_collection.insert_many.return_value = MagicMock(
            inserted_ids=inserted_ids)

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=created_docs)
        mock_mongo_collection.find.return_value = mock_cursor

        result = await investor_repository.bulk_create_investors(investor_inputs)

        assert len(result) == 2
        assert all(isinstance(inv, InvestorResponse) for inv in result)
        assert result[0].name == investor_inputs[0].name
        assert result[1].name == investor_inputs[1].name
        mock_mongo_collection.insert_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_create_investors_empty_list(self, investor_repository):
        """Test bulk create with empty list."""
        result = await investor_repository.bulk_create_investors([])
        assert result == []

    @pytest.mark.asyncio
    async def test_get_investor_by_id_found(self, investor_repository, mock_mongo_collection):
        """Test getting investor by ID when found."""
        sample_doc = MongoInvestorFactory()
        mock_mongo_collection.find_one.return_value = sample_doc

        result = await investor_repository.get_investor_by_id(sample_doc["id"])

        assert result is not None
        assert result.id == sample_doc["id"]
        assert result.name == sample_doc["name"]
        mock_mongo_collection.find_one.assert_called_once_with(
            {"id": sample_doc["id"]})

    @pytest.mark.asyncio
    async def test_get_investor_by_id_not_found(self, investor_repository, mock_mongo_collection):
        """Test getting investor by ID when not found."""
        mock_mongo_collection.find_one.return_value = None

        result = await investor_repository.get_investor_by_id("non-existent")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_commitment_metrics_success(self, investor_repository, mock_mongo_collection):
        """Test updating investor commitment metrics."""
        mock_mongo_collection.update_one.return_value = MagicMock(
            modified_count=1)

        result = await investor_repository.update_commitment_metrics(
            "inv-1", 5, Decimal("1500000.0")
        )

        assert result is True
        mock_mongo_collection.update_one.assert_called_once()
        call_args = mock_mongo_collection.update_one.call_args
        assert call_args[0][0] == {"id": "inv-1"}
        assert call_args[0][1]["$set"]["commitment_count"] == 5
        assert float(call_args[0][1]["$set"]
                     ["total_commitment_amount"]) == 1500000.0
