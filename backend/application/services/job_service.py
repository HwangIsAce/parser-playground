"""Job service for managing async parsing jobs."""
import uuid
from typing import Optional, Dict
from datetime import datetime

from core.models.job import Job, JobStatus
from core.models.parse_result import ParseResult


class JobService:
    """Service for job management operations."""
    
    def __init__(self):
        """Initialize job service."""
        self._jobs: Dict[str, Job] = {}  # In-memory cache
    
    def create_job(
        self,
        document_id: str,
        page_number: int,
        mode: str
    ) -> Job:
        """Create a new parsing job.
        
        Args:
            document_id: Document ID
            page_number: Page number (0-indexed)
            mode: Parse mode ('basic' or 'enhance')
            
        Returns:
            Created Job entity
        """
        job = Job(
            id=str(uuid.uuid4()),
            document_id=document_id,
            page_number=page_number,
            mode=mode,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
        )
        self._jobs[job.id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job entity or None if not found
        """
        return self._jobs.get(job_id)
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[ParseResult] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            result: Parse result (if completed)
            error: Error message (if failed)
            
        Returns:
            True if updated, False if job not found
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        job.status = status
        if status == JobStatus.PROCESSING:
            job.started_at = datetime.now()
        elif status == JobStatus.COMPLETED:
            job.completed_at = datetime.now()
            job.result = result
        elif status == JobStatus.FAILED:
            job.completed_at = datetime.now()
            job.error = error
        
        return True
