"""Tests for Job model."""
import pytest
from datetime import datetime

from core.models.job import Job, JobStatus


class TestJob:
    """Test Job model."""
    
    def test_job_creation(self):
        """Test job creation with default values."""
        job = Job(
            id="test-job-id",
            document_id="doc-123",
            page_number=0,
            mode="basic"
        )
        
        assert job.id == "test-job-id"
        assert job.document_id == "doc-123"
        assert job.page_number == 0
        assert job.mode == "basic"
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
        assert job.metadata == {}
    
    def test_job_is_completed(self):
        """Test job completion check."""
        job = Job(
            id="test-job-id",
            document_id="doc-123",
            page_number=0,
            mode="basic",
            status=JobStatus.COMPLETED
        )
        
        assert job.is_completed() is True
        assert job.is_failed() is False
        assert job.is_finished() is True
    
    def test_job_is_failed(self):
        """Test job failure check."""
        job = Job(
            id="test-job-id",
            document_id="doc-123",
            page_number=0,
            mode="basic",
            status=JobStatus.FAILED,
            error="Test error"
        )
        
        assert job.is_completed() is False
        assert job.is_failed() is True
        assert job.is_finished() is True
    
    def test_job_is_finished(self):
        """Test job finished check."""
        pending_job = Job(
            id="test-job-1",
            document_id="doc-123",
            page_number=0,
            mode="basic",
            status=JobStatus.PENDING
        )
        
        assert pending_job.is_finished() is False
        
        completed_job = Job(
            id="test-job-2",
            document_id="doc-123",
            page_number=0,
            mode="basic",
            status=JobStatus.COMPLETED
        )
        
        assert completed_job.is_finished() is True
