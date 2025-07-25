from unittest.mock import patch

import pytest

from app.services.commitment_service import CommitmentClient
from tests.factories.commitment import make_commitments


class TestCommitmentClient:
    """Test cases for CommitmentClient."""

    @pytest.mark.asyncio
    async def test_get_commitments_success(self, mock_httpx_response_factory):
        client = CommitmentClient()
        expected_data = make_commitments()

        mock_response = mock_httpx_response_factory(
            status=200,
            json_data=expected_data
        )

        with patch.object(client.client, 'get', return_value=mock_response):
            result = await client.get_commitments("inv-1")
            assert result == expected_data

        await client.close()
