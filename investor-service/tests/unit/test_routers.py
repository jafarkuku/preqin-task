from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status

from app.routers.investors import (bulk_create_investors, create_investor,
                                   get_investor, get_investors)
from tests.factories.investor import (InvestorCreateFactory,
                                      InvestorResponseFactory)


class TestInvestorRouters:
    """Test cases for investor API endpoints."""
    @pytest.mark.asyncio
    async def test_bulk_create_investors_success(self):
        """Test successful bulk investor creation."""
        investors_data = InvestorCreateFactory.build_batch(2)
        mock_responses = InvestorResponseFactory.build_batch(2)

        mock_repo = AsyncMock()
        mock_repo.bulk_create_investors.return_value = mock_responses

        result = await bulk_create_investors(investors_data, mock_repo)

        assert len(result) == 2
        assert result[0].name == mock_responses[0].name
        assert result[1].name == mock_responses[1].name

    @pytest.mark.asyncio
    async def test_get_investor_found(self, sample_investor_response):
        """Test getting investor by ID when found."""
        mock_repo = AsyncMock()
        mock_repo.get_investor_by_id.return_value = sample_investor_response

        result = await get_investor("test-inv-123", mock_repo)

        assert result == sample_investor_response
        mock_repo.get_investor_by_id.assert_called_once_with("test-inv-123")

    @pytest.mark.asyncio
    async def test_get_investor_not_found(self):
        """Test getting investor by ID when not found."""
        mock_repo = AsyncMock()
        mock_repo.get_investor_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_investor("non-existent", mock_repo)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Investor with ID non-existent not found" in str(
            exc_info.value.detail)