"""Job API schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from core.models.job import JobStatus
from api.schemas.parse_result import ParseResponse


class JobResponse(BaseModel):
    """Job response schema."""
    
    id: str
    document_id: str
    page_number: int
    mode: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[ParseResponse] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_domain(cls, job) -> "JobResponse":
        """Create response from domain model."""
        return cls(
            id=job.id,
            document_id=job.document_id,
            page_number=job.page_number,
            mode=job.mode,
            status=job.status,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            result=ParseResponse.from_domain(job.result) if job.result else None,
            error=job.error,
        )
