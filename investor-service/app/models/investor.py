"""
Investor models for API validation and database operations.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING


class InvestorType(str, Enum):
    """Valid investor types based on actual data."""
    FUND_MANAGER = "fund manager"
    ASSET_MANAGER = "asset manager"
    WEALTH_MANAGER = "wealth manager"
    BANK = "bank"


class InvestorBase(BaseModel):
    """Base investor model with common fields."""

    name: str = Field(..., min_length=1, max_length=200,
                      description="Investor name")
    investor_type: InvestorType = Field(..., description="Type of investor")
    country: str = Field(..., min_length=2, max_length=100,
                         description="Country name")
    date_added: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date when investor was added"
    )


class InvestorCreate(InvestorBase):
    """Model for creating a new investor via API."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Gryffindor Fund",
                "investor_type": "fund manager",
                "country": "Singapore",
                "date_added": "2024-07-26"
            }
        }
    )


class InvestorResponse(BaseModel):
    """Model for investor API responses."""

    id: str
    name: str
    investor_type: InvestorType
    country: str
    date_added: datetime
    commitment_count: int
    total_commitment_amount: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            InvestorType: lambda v: v.value
        },
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Gryffindor Fund",
                "investor_type": "fund manager",
                "country": "Singapore",
                "date_added": "2024-07-26",
                "commitment_count": 5,
                "total_commitment_amount": 2500000.00,
                "created_at": "2024-07-26T10:30:00",
                "updated_at": "2024-07-26T15:45:00"
            }
        }
    )


class InvestorListResponse(BaseModel):
    """Model for paginated investor list responses."""
    investors: list[InvestorResponse]
    total_commitment_amount: float = Field(
        ..., description="Total commitment amount across all investors in the system")
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=100)
    total_pages: int


class InvestorSummary(BaseModel):
    """Lightweight model for investor summaries."""
    id: str
    name: str
    investor_type: InvestorType
    country: str
    commitment_count: int
    total_commitment_amount: float
    date_added: datetime


INVESTOR_INDEXES = [
    [("id", ASCENDING)],
    [("name", ASCENDING)],
    [("investor_type", ASCENDING)],
    [("country", ASCENDING)],
    [("total_commitment_amount", ASCENDING)],
    [("commitment_count", ASCENDING)],
    [("date_added", ASCENDING)],
    [("created_at", ASCENDING)]
]


def convert_investor_from_db(doc: Optional[dict]) -> Optional[InvestorResponse]:
    """
    Convert a MongoDB document to an InvestorResponse model.
    Returns None if doc is None.
    """
    if doc is None:
        return None

    doc.pop("_id", None)

    # Convert Decimal to float for response if needed
    if "total_commitment_amount" in doc:
        doc["total_commitment_amount"] = float(doc["total_commitment_amount"])

    return InvestorResponse(**doc)


def prepare_investor_for_db(investor: InvestorCreate) -> dict:
    """
    Prepare an investor model for MongoDB insertion.
    Adds computed fields and ensures proper types.
    """
    investor_dict = investor.model_dump()
    now = datetime.now(timezone.utc)
    investor_dict.update({
        "id": str(uuid4()),
        "commitment_count": 0,
        "total_commitment_amount": 0.0,
        "created_at": now,
        "updated_at": now
    })
    return investor_dict
