"""Job service for managing async parsing jobs."""
import uuid
import json
from typing import Optional, Dict
from datetime import datetime

from core.models.job import Job, JobStatus
from core.models.parse_result import ParseResult
from infrastructure.queue.redis_queue import redis_conn


class JobService:
    """Service for job management operations."""
    
    def __init__(self):
        """Initialize job service."""
        self._redis = redis_conn
        self._key_prefix = "job:"
    
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
        key = self._job_key(job.id)
        self._redis.set(key, self._serialize_job(job))
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job entity or None if not found
        """
        key = self._job_key(job_id)
        data = self._redis.get(key)
        if not data:
            return None
        return self._deserialize_job(data)
    
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
        key = self._job_key(job_id)
        data = self._redis.get(key)
        if not data:
            return False
        
        job = self._deserialize_job(data)
        job.status = status
        if status == JobStatus.PROCESSING:
            job.started_at = datetime.now()
        elif status == JobStatus.COMPLETED:
            job.completed_at = datetime.now()
            job.result = result
        elif status == JobStatus.FAILED:
            job.completed_at = datetime.now()
            job.error = error
        
        # Save back to Redis
        self._redis.set(key, self._serialize_job(job))
        return True
    
    def _job_key(self, job_id: str) -> str:
        """Get Redis key for job."""
        return f"{self._key_prefix}{job_id}"
    
    def _serialize_job(self, job: Job) -> bytes:
        """Serialize job to JSON bytes."""
        data = {
            "id": job.id,
            "document_id": job.document_id,
            "page_number": job.page_number,
            "mode": job.mode,
            "status": job.status.value,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "result": job.result.to_dict() if job.result else None,
            "error": job.error,
            "metadata": job.metadata or {},
        }
        return json.dumps(data).encode('utf-8')
    
    def _deserialize_job(self, data: bytes) -> Job:
        """Deserialize job from JSON bytes."""
        job_data = json.loads(data.decode('utf-8'))
        
        # Deserialize ParseResult if present
        result = None
        if job_data.get("result"):
            from core.models.parse_result import ParseResult as ParseResultModel
            result = ParseResultModel.from_dict(job_data["result"])
        
        return Job(
            id=job_data["id"],
            document_id=job_data["document_id"],
            page_number=job_data["page_number"],
            mode=job_data["mode"],
            status=JobStatus(job_data["status"]),
            created_at=datetime.fromisoformat(job_data["created_at"]) if job_data.get("created_at") else None,
            started_at=datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None,
            completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
            result=result,
            error=job_data.get("error"),
            metadata=job_data.get("metadata", {}),
        )
