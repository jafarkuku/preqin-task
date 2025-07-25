from unittest.mock import patch

import pytest

from app.services.investor_service import InvestorClient
from tests.factories.investor import make_investors


class TestInvestorClientService:
    """Test cases for InvestorClient."""

    @pytest.mark.asyncio
    async def test_get_all_investors_success(self, mock_httpx_response_factory):
        """Test successful get_all_investors call."""
        client = InvestorClient()
        expected_data = make_investors(count=1)

        mock_response = mock_httpx_response_factory(
            status=200, json_data=expected_data
        )

        with patch.object(client.client, 'get', return_value=mock_response):
            result = await client.get_all_investors(1, 20)
            assert result == expected_data

        await client.close()

    @pytest.mark.asyncio
    async def test_get_investor_not_found(self, mock_httpx_404_response):
        """Test get_investor with 404 response."""
        client = InvestorClient()

        with patch.object(client.client, 'get', return_value=mock_httpx_404_response):
            result = await client.get_investor("invalid-id")
            assert result is None

        await client.close()

    @pytest.mark.asyncio
    async def test_get_investor_network_error(self, mock_httpx_network_error):
        """Test get_investor with network error."""
        client = InvestorClient()

        with patch.object(client.client, 'get', side_effect=mock_httpx_network_error):
            result = await client.get_investor("inv-1")
            assert result is None

        await client.close()
