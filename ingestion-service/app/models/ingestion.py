# """
# Pydantic models for ingestion service.
# """

# from datetime import datetime
# from enum import Enum
# from typing import List, Optional, Dict, Any
# from pydantic import BaseModel, Field


# class IngestionStatus(str, Enum):
#     """Status of an ingestion job."""
#     PENDING = "pending"
#     PROCESSING = "processing"
#     COMPLETED = "completed"
#     FAILED = "failed"


# class IngestionJob(BaseModel):
#     """Ingestion job model."""

#     job_id: str
#     status: IngestionStatus
#     filename: Optional[str] = None
#     started_at: datetime
#     completed_at: Optional[datetime] = None
#     total_rows: Optional[int] = None
#     processed_rows: Optional[int] = None
#     errors: List[str] = Field(default_factory=list)
