"""
Commitment models for pure commitment service.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class Currency(str, Enum):
    """Supported currencies."""
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"


class CommitmentBase(BaseModel):
    """Base commitment model with common fields."""

    investor_id: str = Field(..., description="Investor identifier")
    asset_class_id: str = Field(..., description="Asset class identifier")
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2,
                            description="Commitment amount")
    currency: Currency = Field(
        default=Currency.GBP, description="Currency code")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive and has max 2 decimal places."""
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class CommitmentCreate(CommitmentBase):
    """Model for creating a new commitment via API."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "investor_id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_class_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                "amount": 1000000.00,
                "currency": "GBP"
            }
        }
    )


class CommitmentResponse(BaseModel):
    """Simple commitment model - pure commitment data only."""

    id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: Currency
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra={
            "example": {
                "id": "456e7890-e12b-34c5-d678-901234567890",
                "investor_id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_class_id": "987fcdeb-51d2-43a1-b789-123456789abc",
                "amount": 1000000.00,
                "currency": "GBP",
                "created_at": "2024-07-26T10:30:00Z",
                "updated_at": "2024-07-26T10:30:00Z"
            }
        }
    )


class CommitmentSummaryResult(BaseModel):
    """Type definition for commitment summary for an investor."""
    count: int
    total_amount: float


class AssetBreakdown(BaseModel):
    """Asset class breakdown for an investor."""
    asset_class_id: str
    total_amount: float
    commitment_count: int
    percentage_of_total: float


class CommitmentListResponse(BaseModel):
    """Model for paginated commitment list responses."""

    commitments: List[CommitmentResponse]
    asset_breakdowns: List[AssetBreakdown]
    total: int
    total_amount: float
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=100)
    total_pages: int
    has_next: bool
    has_prev: bool


class CommitmentCreatedEvent(BaseModel):
    event_type: str = "commitment_created"
    commitment_id: str
    investor_id: str
    asset_class_id: str
    amount: float
    currency: str


def convert_commitment_from_db(row: Optional[dict]) -> Optional[CommitmentResponse]:
    """
    Convert a SQLite row to a CommitmentResponse model.

    Handles type conversions and field mapping.
    """
    if row is None:
        return None

    try:
        if "amount" in row:
            row["amount"] = float(row["amount"])

        for field in ["created_at", "updated_at"]:
            if field in row and isinstance(row[field], str):
                row[field] = datetime.fromisoformat(
                    row[field].replace('Z', '+00:00'))

        return CommitmentResponse(**row)
    except Exception as e:
        logger.error("Error converting commitment from DB: %s", e)
        return None


def prepare_commitment_for_db(commitment: CommitmentCreate) -> dict:
    """
    Prepare a commitment model for SQLite insertion.
    """
    commitment_dict = commitment.model_dump()

    now = datetime.now(timezone.utc)
    commitment_dict.update({
        "id": str(uuid4()),
        "created_at": now,
        "updated_at": now
    })

    commitment_dict["amount"] = float(commitment_dict["amount"])

    return commitment_dict
