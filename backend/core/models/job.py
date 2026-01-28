"""Job domain model for async parsing tasks."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from core.models.parse_result import ParseResult


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Job entity for async parsing tasks."""
    
    id: str
    document_id: str
    page_number: int
    mode: str  # 'basic' or 'enhance'
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[ParseResult] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def is_completed(self) -> bool:
        """Check if job is completed."""
        return self.status == JobStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == JobStatus.FAILED
    
    def is_finished(self) -> bool:
        """Check if job is finished (completed or failed)."""
        return self.is_completed() or self.is_failed()
