"""
Enhanced Asset Class router with bulk fetch endpoint.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Query, status

from app.models.asset_class import (AssetClassCreate, AssetClassCreateResponse,
                                    AssetClassListResponse, AssetClassResponse)
from app.repositories.asset_class_repository import asset_class_repository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/asset-classes",
    tags=["asset-classes"],
    responses={
        404: {"description": "Asset class not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/bulk",
    response_model=List[AssetClassResponse],
    summary="Bulk fetch asset classes by IDs",
    description="Fetch multiple asset classes by their IDs in a single request."
)
async def bulk_get_asset_classes(
    asset_class_ids: List[str] = Body(...,
                                      description="List of asset class IDs to fetch")
):
    """
    Bulk fetch asset classes by their IDs.
    """
    try:
        if not asset_class_ids:
            return []

        if len(asset_class_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 asset class IDs allowed per bulk request"
            )

        logger.info("Bulk fetching %d asset classes", len(asset_class_ids))

        asset_classes = await asset_class_repository.get_by_ids(asset_class_ids)

        logger.info("Successfully fetched %d/%d asset classes",
                    len(asset_classes), len(asset_class_ids))

        return [AssetClassResponse(**ac.model_dump()) for ac in asset_classes]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error bulk fetching asset classes: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e


@router.post(
    "",
    response_model=AssetClassCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new asset class",
    description="Create a new asset class with the provided information."
)
async def create_asset_class(asset_class: AssetClassCreate):
    """
    Create a new asset class.
    """
    try:
        existing = await asset_class_repository.get_by_name(asset_class.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset class with name '{asset_class.name}' already exists"
            )

        created_asset_class = await asset_class_repository.create(asset_class)

        if not created_asset_class:
            logger.error("Failed to create investor: %s", asset_class.name)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create investor"
            )

        response_data = AssetClassResponse(
            **created_asset_class.model_dump())

        return AssetClassCreateResponse(data=response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating asset class: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e


@router.get(
    "/",
    response_model=List[AssetClassResponse],
    summary="List all asset classes",
    description="Get a paginated list of asset classes with optional filtering."
)
async def list_asset_classes():
    """
    Get a list of asset classes with pagination and filtering.
    """
    try:
        asset_classes = await asset_class_repository.get_all()

        response_data = [
            AssetClassResponse(**asset_class.model_dump()) for asset_class in asset_classes
        ]

        return response_data

    except Exception as e:
        logger.error("Error listing asset classes: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e


@router.post(
    "/bulk-create",
    response_model=List[AssetClassResponse],
    summary="Bulk create asset classes",
    description="Create multiple asset classes in a single request for efficient batch processing."
)
async def bulk_create_asset_classes(
    asset_classes_data: List[AssetClassCreate] = Body(...,
                                                      description="List of asset classes to create")
) -> List[AssetClassResponse]:
    """
    Bulk create asset classes for efficient ingestion.
    """
    try:
        if not asset_classes_data:
            return []

        if len(asset_classes_data) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 asset classes allowed per bulk request"
            )

        logger.info("Bulk creating %d asset classes", len(asset_classes_data))

        created_asset_classes = await asset_class_repository.bulk_create(asset_classes_data)

        logger.info("Successfully bulk created %d/%d asset classes",
                    len(created_asset_classes), len(asset_classes_data))

        return [AssetClassResponse(**ac.model_dump()) for ac in created_asset_classes]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error bulk creating asset classes: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while bulk creating asset classes"
        ) from e
