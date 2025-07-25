# pyright: reportGeneralTypeIssues=false
# pyright: reportArgumentType=false
from unittest.mock import patch

import pytest

from app.schema.commitments import CommitmentQueries
from tests.factories.asset_class import make_asset_classes
from tests.factories.commitment import make_commitments
from tests.factories.investor import make_investors


class TestCommitmentQueries:
    """Test cases for commitment GraphQL queries."""

    @pytest.mark.asyncio
    async def test_commitment_breakdown_success(
        self,
        mock_investor_client,
        mock_commitment_client,
        mock_asset_class_client
    ):
        """Test successful commitment breakdown query."""
        test_investor = {
            "id": "inv-1",
            "name": "Test Investor 1",
            "investor_type": "Pension Fund",
            "country": "USA",
            "date_added": "2024-01-01",
            "commitment_count": 3,
            "total_commitment_amount": 1500000.0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

        investors = make_investors(count=1, overrides=[test_investor])
        mock_investor_client.get_all_investors.return_value = investors
        mock_investor_client.get_investor.return_value = test_investor
        mock_commitment_client.get_commitments.return_value = make_commitments()
        mock_asset_class_client.get_asset_classes.return_value = make_asset_classes()

        with patch('app.schema.commitments.get_investor_client', return_value=mock_investor_client), \
                patch('app.schema.commitments.get_commitment_client', return_value=mock_commitment_client), \
                patch('app.schema.commitments.get_asset_class_client', return_value=mock_asset_class_client):

            query = CommitmentQueries()
            result = await query.commitment_breakdown("inv-1")

            assert result is not None
            assert result.investor_id == "inv-1"
            assert result.investor_name == "Test Investor 1"
            assert result.total_commitment_amount == 1500000.0

    @pytest.mark.asyncio
    async def test_commitment_breakdown_investor_not_found(self, mock_investor_client, mock_commitment_client):
        """Test commitment breakdown when investor not found."""
        mock_investor_client.get_investor.return_value = None

        with patch('app.schema.commitments.get_investor_client', return_value=mock_investor_client), \
                patch('app.schema.commitments.get_commitment_client', return_value=mock_commitment_client):

            query = CommitmentQueries()
            result = await query.commitment_breakdown("invalid-id")

            assert result is None

    @pytest.mark.asyncio
    async def test_commitment_breakdown_no_commitments(self, mock_investor_client, mock_commitment_client):
        """Test commitment breakdown with no commitments."""
        mock_commitment_client.get_commitments.return_value = {
            "commitments": [],
            "total": 0,
            "total_amount": 0.0,
            "page": 1,
            "size": 100,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False
        }

        with patch('app.schema.commitments.get_investor_client', return_value=mock_investor_client), \
                patch('app.schema.commitments.get_commitment_client', return_value=mock_commitment_client):

            query = CommitmentQueries()
            result = await query.commitment_breakdown("inv-1")

            assert result.investor_id == "inv-1"
            assert result.total_commitment_amount == 0.0
            assert len(result.commitments) == 0
            assert len(result.assets) == 0

    @pytest.mark.asyncio
    async def test_commitment_breakdown_asset_class_fetch_error(self, mock_investor_client, mock_commitment_client, mock_asset_class_client):
        """Test commitment breakdown when asset class fetch fails."""
        mock_asset_class_client.get_asset_classes.return_value = None

        with patch('app.schema.commitments.get_investor_client', return_value=mock_investor_client), \
                patch('app.schema.commitments.get_commitment_client', return_value=mock_commitment_client), \
                patch('app.schema.commitments.get_asset_class_client', return_value=mock_asset_class_client):

            query = CommitmentQueries()
            result = await query.commitment_breakdown("inv-1")

            assert result is not None
            assert len(result.commitments) == 2
            assert "Unknown Asset Class" in result.commitments[0].name
