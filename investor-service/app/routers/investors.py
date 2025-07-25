"""
Enhanced Investor router with bulk fetch endpoint.
"""
import logging
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.models.investor import (InvestorCreate, InvestorListResponse,
                                 InvestorResponse)
from app.repositories import get_investor_repository
from app.repositories.investor_repository import InvestorRepository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/investors",
    tags=["investors"],
    responses={
        404: {"description": "Investor not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/",
    response_model=InvestorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investor",
    description="Create a new investor with the provided information."
)
async def create_investor(
    investor_data: InvestorCreate,
    repo: InvestorRepository = Depends(get_investor_repository)
) -> InvestorResponse:
    """
    Create a new investor.
    """
    try:
        logger.info("Creating new investor: %s", investor_data.name)

        created_investor = await repo.create_investor(investor_data)

        if not created_investor:
            logger.error("Failed to create investor: %s", investor_data.name)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create investor"
            )

        logger.info("Successfully created investor with ID: %s",
                    created_investor.id)
        return created_investor

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating investor: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating investor"
        ) from e


@router.post(
    "/bulk-create",
    response_model=List[InvestorResponse],
    summary="Bulk create investors",
    description="Create multiple investors in a single request for efficient batch processing."
)
async def bulk_create_investors(
    investors_data: List[InvestorCreate] = Body(...,
                                                description="List of investors to create"),
    repo: InvestorRepository = Depends(get_investor_repository)
) -> List[InvestorResponse]:
    """
    Bulk create investors for efficient ingestion.
    """
    try:
        if not investors_data:
            return []

        if len(investors_data) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 500 investors allowed per bulk request"
            )

        logger.info("Bulk creating %d investors", len(investors_data))

        # Use repository bulk method
        created_investors = await repo.bulk_create_investors(investors_data)

        logger.info("Successfully bulk created %d/%d investors",
                    len(created_investors), len(investors_data))

        return created_investors

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error bulk creating investors: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while bulk creating investors"
        ) from e


@router.get(
    "/{investor_id}",
    response_model=InvestorResponse,
    summary="Get investor by ID",
    description="Retrieve a specific investor by their unique identifier."
)
async def get_investor(
    investor_id: str,
    repo: InvestorRepository = Depends(get_investor_repository)
) -> InvestorResponse:
    """
    Get a specific investor by ID.
    """
    try:
        logger.info("Fetching investor with ID: %s", investor_id)

        investor = await repo.get_investor_by_id(investor_id)

        if not investor:
            logger.warning("Investor not found: %s", investor_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investor with ID {investor_id} not found"
            )

        return investor

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching investor %s: %s",
                     investor_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching investor"
        ) from e


@router.get(
    "/",
    response_model=InvestorListResponse,
    summary="List all investors",
    description="Get a paginated list of all investors with optional sorting."
)
async def get_investors(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    size: int = Query(20, ge=1, le=100,
                      description="Number of items per page"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order: asc or desc"),
    repo: InvestorRepository = Depends(get_investor_repository)
) -> InvestorListResponse:
    """
    Get a paginated list of all investors.
    """
    try:
        skip = (page - 1) * size

        logger.info("Fetching investors page %d (size: %d)", page, size)

        result = await repo.get_all_investors(
            skip=skip,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return InvestorListResponse(**result)

    except Exception as e:
        logger.error("Error fetching investors: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching investors"
        ) from e
