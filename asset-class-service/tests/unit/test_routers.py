from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.models.asset_class import AssetClassCreate, AssetClassResponse


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_repository():
    """Mock asset class repository."""
    return AsyncMock()


class TestAssetClassRouters:
    """Test cases for asset class API endpoints."""

    @pytest.mark.asyncio
    async def test_bulk_get_asset_classes_success(self, mock_repository):
        """Test successful bulk fetch endpoint."""

        asset_class_ids = ["id1", "id2"]
        mock_responses = [
            AssetClassResponse(
                id="id1", name="PE", description="Private Equity", status="active",
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            ),
            AssetClassResponse(
                id="id2", name="RE", description="Real Estate", status="active",
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            )
        ]
        mock_repository.get_by_ids.return_value = mock_responses

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_get_asset_classes
            result = await bulk_get_asset_classes(asset_class_ids)

            assert len(result) == 2
            assert result[0].name == "PE"
            assert result[1].name == "RE"
            mock_repository.get_by_ids.assert_called_once_with(asset_class_ids)

    @pytest.mark.asyncio
    async def test_bulk_get_asset_classes_empty_list(self, mock_repository):
        """Test bulk fetch with empty list."""

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_get_asset_classes
            result = await bulk_get_asset_classes([])

            assert result == []
            mock_repository.get_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_get_asset_classes_too_many_ids(self, mock_repository):
        """Test bulk fetch with too many IDs."""

        asset_class_ids = [f"id{i}" for i in range(101)]  # 101 IDs

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_get_asset_classes

            with pytest.raises(HTTPException) as exc_info:
                await bulk_get_asset_classes(asset_class_ids)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Maximum 100 asset class IDs allowed" in str(
                exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_asset_class_success(self, mock_repository):
        """Test successful asset class creation."""

        asset_class_data = AssetClassCreate(
            name="Test PE", description="Test", status="active")
        mock_response = AssetClassResponse(
            id="test-id", name="Test PE", description="Test", status="active",
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )

        mock_repository.get_by_name.return_value = None  # No existing asset class
        mock_repository.create.return_value = mock_response

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import create_asset_class
            result = await create_asset_class(asset_class_data)

            assert result.data.name == "Test PE"
            assert result.message == "Asset class created successfully"
            mock_repository.get_by_name.assert_called_once_with("Test PE")
            mock_repository.create.assert_called_once_with(asset_class_data)

    @pytest.mark.asyncio
    async def test_create_asset_class_duplicate_name(self, mock_repository):
        """Test creating asset class with duplicate name."""

        asset_class_data = AssetClassCreate(
            name="Existing PE", description="Test", status="active")
        existing_asset_class = AssetClassResponse(
            id="existing-id", name="Existing PE", description="Existing", status="active",
            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
        )
        mock_repository.get_by_name.return_value = existing_asset_class

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import create_asset_class

            with pytest.raises(HTTPException) as exc_info:
                await create_asset_class(asset_class_data)

            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "already exists" in str(exc_info.value.detail)
            mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_asset_class_creation_failure(self, mock_repository):
        """Test asset class creation failure."""

        asset_class_data = AssetClassCreate(
            name="Test PE", description="Test", status="active")
        mock_repository.get_by_name.return_value = None
        mock_repository.create.return_value = None  # Creation failed

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import create_asset_class

            with pytest.raises(HTTPException) as exc_info:
                await create_asset_class(asset_class_data)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_list_asset_classes_success(self, mock_repository):
        """Test successful asset class listing."""

        mock_responses = [
            AssetClassResponse(
                id="id1", name="PE", description="Private Equity", status="active",
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            )
        ]
        mock_repository.get_all.return_value = mock_responses
        mock_repository.count.return_value = 1

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import list_asset_classes
            result = await list_asset_classes(skip=0, limit=10, asset_status="active")

            assert len(result.data) == 1
            assert result.total == 1
            assert result.page == 1
            assert result.size == 10
            mock_repository.get_all.assert_called_once_with(
                skip=0, limit=10, status="active")
            mock_repository.count.assert_called_once_with(status="active")

    @pytest.mark.asyncio
    async def test_bulk_create_asset_classes_success(self, mock_repository):
        """Test successful bulk creation."""

        asset_classes_data = [
            AssetClassCreate(
                name="PE", description="Private Equity", status="active"),
            AssetClassCreate(
                name="RE", description="Real Estate", status="active")
        ]
        mock_responses = [
            AssetClassResponse(
                id="id1", name="PE", description="Private Equity", status="active",
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            ),
            AssetClassResponse(
                id="id2", name="RE", description="Real Estate", status="active",
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
            )
        ]
        mock_repository.bulk_create.return_value = mock_responses

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_create_asset_classes
            result = await bulk_create_asset_classes(asset_classes_data)

            assert len(result) == 2
            assert result[0].name == "PE"
            assert result[1].name == "RE"
            mock_repository.bulk_create.assert_called_once_with(
                asset_classes_data)

    @pytest.mark.asyncio
    async def test_bulk_create_asset_classes_empty_list(self, mock_repository):
        """Test bulk creation with empty list."""

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_create_asset_classes
            result = await bulk_create_asset_classes([])

            assert result == []
            mock_repository.bulk_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_create_asset_classes_too_many(self, mock_repository):
        """Test bulk creation with too many items."""

        asset_classes_data = [
            AssetClassCreate(
                name=f"AC{i}", description="Test", status="active")
            for i in range(101)
        ]

        with patch('app.routers.asset_classes.asset_class_repository', mock_repository):
            from app.routers.asset_classes import bulk_create_asset_classes

            with pytest.raises(HTTPException) as exc_info:
                await bulk_create_asset_classes(asset_classes_data)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Maximum 100 asset classes allowed" in str(
                exc_info.value.detail)
