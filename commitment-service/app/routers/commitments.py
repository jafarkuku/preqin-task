"""
FastAPI router for commitment endpoints.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.models.commitment import (CommitmentCreate, CommitmentListResponse,
                                   CommitmentResponse)
from app.repositories import get_commitment_repository
from app.repositories.commitment_repository import CommitmentRepository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/commitments",
    tags=["commitments"],
    responses={
        404: {"description": "Commitment not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/",
    response_model=CommitmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new commitment",
    description="Create a new commitment. Validation of investor/asset class IDs happens at gateway level."
)
async def create_commitment(
    commitment_data: CommitmentCreate,
    repo: CommitmentRepository = Depends(get_commitment_repository)
) -> CommitmentResponse:
    """
    Create a new commitment - simplified without external validation.

    The gateway is responsible for validating investor_id and asset_class_id exist.
    This service focuses purely on commitment CRUD operations.

    Args:
        commitment_data: Commitment information to create
        repo: Injected repository dependency

    Returns:
        CommitmentResponse: Created commitment information

    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info("Creating new commitment for investor: %s",
                    commitment_data.investor_id)

        created_commitment = await repo.create_commitment(commitment_data)

        if not created_commitment:
            logger.error("Failed to create commitment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create commitment"
            )

        logger.info("Successfully created commitment with ID: %s",
                    created_commitment.id)
        return created_commitment

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating commitment: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating commitment"
        ) from e


@router.get(
    "/{commitment_id}",
    response_model=CommitmentResponse,
    summary="Get commitment by ID",
    description="Retrieve a specific commitment by its unique identifier."
)
async def get_commitment(
    commitment_id: str,
    repo: CommitmentRepository = Depends(get_commitment_repository)
) -> CommitmentResponse:
    """Get a specific commitment by ID."""
    try:
        logger.info("Fetching commitment with ID: %s", commitment_id)

        commitment = await repo.get_commitment_by_id(commitment_id)

        if not commitment:
            logger.warning("Commitment not found: %s", commitment_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Commitment with ID {commitment_id} not found"
            )

        return commitment

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching commitment %s: %s",
                     commitment_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching commitment"
        ) from e


@router.get(
    "/",
    response_model=CommitmentListResponse,
    summary="List commitments",
    description="Get a paginated list of commitments with optional filtering."
)
async def list_commitments(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    size: int = Query(20, ge=1, le=100,
                      description="Number of items per page"),
    investor_id: Optional[str] = Query(
        None, description="Filter by investor ID"),
    asset_class_id: Optional[str] = Query(
        None, description="Filter by asset class ID"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$",
                            description="Sort order"),
    repo: CommitmentRepository = Depends(get_commitment_repository)
) -> CommitmentListResponse:
    """Get a paginated list of commitments with filtering."""
    try:
        skip = (page - 1) * size

        logger.info("Fetching commitments page %d (size: %d)", page, size)

        result = await repo.get_commitments(
            skip=skip,
            limit=size,
            investor_id=investor_id,
            asset_class_id=asset_class_id,
            currency=currency,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return CommitmentListResponse(**result)

    except Exception as e:
        logger.error("Error fetching commitments: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching commitments"
        ) from e


@router.post(
    "/bulk-create",
    summary="Bulk create commitments",
    description="Create multiple commitments in a single request"
)
async def bulk_create(
    commitments_data: list[CommitmentCreate] = Body(
        ..., description="List of commitments to create"),
    repo: CommitmentRepository = Depends(get_commitment_repository)
) -> list[CommitmentResponse]:
    """
    Bulk create commitments for efficient ingestion.

    This endpoint is optimized for ingestion service bulk operations.

    - **commitments_data**: List of commitment data to create

    Returns:
        List of created commitments
    """
    try:
        if not commitments_data:
            return []

        logger.info("Bulk creating %d commitments", len(commitments_data))

        created_commitments = await repo.bulk_create_commitments(commitments_data)

        logger.info("Successfully bulk created %d/%d commitments",
                    len(created_commitments), len(commitments_data))

        return created_commitments
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error bulk creating commitments: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while bulk creating commitments"
        ) from e
