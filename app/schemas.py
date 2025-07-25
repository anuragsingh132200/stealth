from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class OperationType(str, Enum):
    SQUARE_SUM = "square_sum"
    CUBE_SUM = "cube_sum"

class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class JobCreate(BaseModel):
    data: List[float] = Field(..., description="List of numbers to process")
    operation: OperationType = Field(..., description="Type of operation to perform")

class JobResponse(BaseModel):
    id: int
    status: JobStatus
    operation: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobStatusResponse(JobResponse):
    pass

class JobResultResponse(JobResponse):
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None