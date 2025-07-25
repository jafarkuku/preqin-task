# pyright: reportCallIssue=false

from unittest.mock import patch

import pytest

from app.schema.investors import InvestorQueries
from tests.factories.investor import make_investors


class TestInvestorQueries:
    """Test cases for investor GraphQL queries."""

    @pytest.mark.asyncio
    async def test_investors_query_success(self, mock_investor_client):
        """Test successful investors list query."""
        expected_data = make_investors()
        mock_investor_client.get_all_investors.return_value = expected_data

        with patch('app.schema.investors.get_investor_client', return_value=mock_investor_client):
            query = InvestorQueries()
            result = await query.investors(page=1, size=20)

            assert len(result.investors) == expected_data["total"]
            assert result.total_commitment_amount == expected_data["total_commitment_amount"]
            assert result.total == expected_data["total"]
            assert result.page == expected_data["page"]
            assert result.size == expected_data["size"]
            assert result.total_pages == expected_data["total_pages"]

            investor1 = result.investors[0]
            expected_investor1 = expected_data["investors"][0]

            assert investor1.id == expected_investor1["id"]
            assert investor1.name == expected_investor1["name"]
            assert investor1.investor_type == expected_investor1["investor_type"]
            assert investor1.commitment_count == expected_investor1["commitment_count"]
            assert investor1.total_commitment_amount == expected_investor1[
                "total_commitment_amount"]

    @pytest.mark.asyncio
    async def test_investors_query_empty_response(self, mock_investor_client):
        """Test investors query with empty response."""
        mock_investor_client.get_all_investors.return_value = None

        with patch('app.schema.investors.get_investor_client', return_value=mock_investor_client):
            query = InvestorQueries()
            result = await query.investors()

            assert len(result.investors) == 0
            assert result.total_commitment_amount == 0.0
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_investors_query_exception(self, mock_investor_client):
        """Test investors query error handling."""
        mock_investor_client.get_all_investors.side_effect = Exception(
            "Service error")

        with patch('app.schema.investors.get_investor_client', return_value=mock_investor_client):
            query = InvestorQueries()
            result = await query.investors()

            # Should return empty result on error
            assert len(result.investors) == 0
            assert result.total_commitment_amount == 0.0
            assert result.total == 0
