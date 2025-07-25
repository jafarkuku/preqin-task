from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

from pymongo import ASCENDING


class AssetClassStatus(str, Enum):
    """Valid asset class status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class AssetClassBase(BaseModel):
    """
    Base model containing common fields for asset class.
    """
    name: str = Field(..., min_length=1, max_length=100,
                      description="Asset class name")
    description: Optional[str] = Field(
        None, max_length=500, description="Asset class description")
    status: str = Field(
        default=AssetClassStatus.ACTIVE, description="Asset class status")


class AssetClassCreate(AssetClassBase):
    """
    Model for creating a new asset class.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Private Equity",
                "description": "Private equity investments including buyouts and growth capital",
                "status": "active"
            }
        }
    )


class AssetClassInDB(AssetClassBase):
    """
    Model representing how asset class is stored in the database.
    """
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                 description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                 description="Last update timestamp")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            AssetClassStatus: lambda v: v.value
        }
    )


class AssetClassResponse(BaseModel):
    """
    Model for API responses.
    """
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            AssetClassStatus: lambda v: v.value
        },
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Private Equity",
                "description": "Private equity investments including buyouts and growth capital",
                "status": "active",
                "created_at": "2024-07-26T10:30:00Z",
                "updated_at": "2024-07-26T15:45:00Z"
            }
        }
    )


class AssetClassListResponse(BaseModel):
    """
    Model for paginated list responses.
    """
    data: list[AssetClassResponse]
    total: int
    page: int = 1
    size: int = 100

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Private Equity",
                        "description": "Private equity investments",
                        "status": "active",
                        "created_at": "2024-07-26T10:30:00Z",
                        "updated_at": "2024-07-26T15:45:00Z"
                    }
                ],
                "total": 25,
                "page": 1,
                "size": 10,
                "total_pages": 3
            }
        }
    )


class AssetClassCreateResponse(BaseModel):
    """
    Response model for create operations.
    """
    message: str = "Asset class created successfully"
    data: AssetClassResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Asset class created successfully",
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Private Equity",
                    "description": "Private equity investments",
                    "status": "active",
                    "created_at": "2024-07-26T10:30:00Z",
                    "updated_at": "2024-07-26T15:45:00Z"
                }
            }
        }
    )


def convert_asset_class_from_db(doc: dict) -> Optional[AssetClassResponse]:
    """
    Convert a MongoDB document to an AssetClassResponse model.
    """
    if doc is None:
        return None

    doc.pop("_id", None)

    return AssetClassResponse(**doc)


def prepare_asset_class_for_db(asset_class: AssetClassCreate) -> dict:
    """
    Prepare an asset class model for MongoDB insertion.
    """
    asset_class_dict = asset_class.model_dump()

    asset_class_dict.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })

    return asset_class_dict
