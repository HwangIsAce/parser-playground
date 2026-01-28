"""Tests for JobService."""
import pytest

from application.services.job_service import JobService
from core.models.job import JobStatus
from core.models.parse_result import ParseResult, Block


class TestJobService:
    """Test JobService."""
    
    def test_create_job(self):
        """Test job creation."""
        service = JobService()
        
        job = service.create_job("doc-123", 0, "basic")
        
        assert job.id is not None
        assert job.document_id == "doc-123"
        assert job.page_number == 0
        assert job.mode == "basic"
        assert job.status == JobStatus.PENDING
    
    def test_get_job(self):
        """Test job retrieval."""
        service = JobService()
        
        job = service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        retrieved_job = service.get_job(job_id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == job_id
        assert retrieved_job.document_id == "doc-123"
    
    def test_get_nonexistent_job(self):
        """Test retrieval of nonexistent job."""
        service = JobService()
        
        job = service.get_job("nonexistent-id")
        
        assert job is None
    
    def test_update_job_status_to_processing(self):
        """Test updating job status to processing."""
        service = JobService()
        
        job = service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        updated = service.update_job_status(job_id, JobStatus.PROCESSING)
        
        assert updated is True
        updated_job = service.get_job(job_id)
        assert updated_job.status == JobStatus.PROCESSING
        assert updated_job.started_at is not None
    
    def test_update_job_status_to_completed(self):
        """Test updating job status to completed."""
        service = JobService()
        
        job = service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        parse_result = ParseResult(
            document_id="doc-123",
            blocks=[Block(type="text", text="Test")],
            metadata={}
        )
        
        updated = service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result=parse_result
        )
        
        assert updated is True
        updated_job = service.get_job(job_id)
        assert updated_job.status == JobStatus.COMPLETED
        assert updated_job.completed_at is not None
        assert updated_job.result == parse_result
    
    def test_update_job_status_to_failed(self):
        """Test updating job status to failed."""
        service = JobService()
        
        job = service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        updated = service.update_job_status(
            job_id,
            JobStatus.FAILED,
            error="Test error"
        )
        
        assert updated is True
        updated_job = service.get_job(job_id)
        assert updated_job.status == JobStatus.FAILED
        assert updated_job.completed_at is not None
        assert updated_job.error == "Test error"
    
    def test_update_nonexistent_job(self):
        """Test updating nonexistent job."""
        service = JobService()
        
        updated = service.update_job_status(
            "nonexistent-id",
            JobStatus.COMPLETED
        )
        
        assert updated is False
