"""Job API routes for polling job status."""
from fastapi import APIRouter, HTTPException

from api.schemas.job import JobResponse
from application.services.job_service import JobService

router = APIRouter()

# Shared instance (same as in parse.py)
# Note: In production, this should be a proper singleton or dependency injection
_job_service_instance = None

def get_job_service() -> JobService:
    """Get shared JobService instance."""
    global _job_service_instance
    if _job_service_instance is None:
        _job_service_instance = JobService()
    return _job_service_instance

job_service = get_job_service()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get job status (for polling).
    
    Args:
        job_id: Job ID
        
    Returns:
        JobResponse with current status
        
    Note:
        - Used for polling job completion
        - Returns 404 if job not found
    """
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.from_domain(job)
