from unittest.mock import patch

import pytest

from app.services.asset_class_service import AssetClassClient
from tests.factories.asset_class import make_asset_classes


class TestAssetClassClient:
    """Test cases for AssetClassClient."""

    @pytest.mark.asyncio
    async def test_get_asset_classes_success(self, mock_httpx_response_factory):
        """Test get asset classes"""
        client = AssetClassClient()

        asset_classes = make_asset_classes()
        mock_response = mock_httpx_response_factory(
            status=200, json_data=asset_classes)

        with patch.object(client.client, 'post', return_value=mock_response) as mock_post:
            result = await client.get_asset_classes(["ac-1", "ac-2"])

            assert result == asset_classes
            mock_post.assert_called_once_with(
                f"{client.base_url}/api/asset-classes/bulk",
                json=["ac-1", "ac-2"]
            )

        await client.close()
