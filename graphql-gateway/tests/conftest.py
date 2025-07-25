from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from tests.factories.asset_class import make_asset_classes
from tests.factories.commitment import make_commitments
from tests.factories.investor import make_investors


@pytest.fixture
def mock_investor_client():
    """Mock InvestorClient for testing."""
    client = AsyncMock()
    investor_payload = make_investors()

    client.get_all_investors.return_value = investor_payload
    client.get_investor.return_value = investor_payload["investors"][0]

    return client


@pytest.fixture
def mock_commitment_client():
    """Mock CommitmentClient using factory-generated commitments."""
    client = AsyncMock()
    client.get_commitments.return_value = make_commitments()
    return client


@pytest.fixture
def mock_asset_class_client():
    """Mock AssetClassClient using factory-generated asset classes."""
    client = AsyncMock()
    client.get_asset_classes.return_value = make_asset_classes()
    return client


@pytest.fixture
def mock_httpx_response_factory():
    """
    Factory to create a mocked httpx.AsyncClient response.
    """
    def _make_mock_response(status: int = 200, json_data=None):
        response = AsyncMock()
        response.status_code = status
        response.json = MagicMock(return_value=json_data)
        return response

    return _make_mock_response


@pytest.fixture
def mock_httpx_404_response():
    """Mock 404 response."""
    response = AsyncMock()
    response.status_code = 404
    return response


@pytest.fixture
def mock_httpx_network_error():
    """Simulate a network error for httpx request."""
    return httpx.RequestError("Simulated network error")
