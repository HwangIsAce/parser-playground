"""Tests for Jobs API."""
import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.routes.jobs import get_job_service
from core.models.job import JobStatus
from core.models.parse_result import ParseResult, Block


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def job_service():
    """Get shared job service instance (same as API)."""
    return get_job_service()


class TestJobsAPI:
    """Test Jobs API endpoints."""
    
    def test_get_job_not_found(self, client):
        """Test getting nonexistent job."""
        response = client.get("/api/v1/jobs/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_job_success(self, client, job_service):
        """Test getting existing job."""
        # Create a job
        job = job_service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        # Get job via API
        response = client.get(f"/api/v1/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["document_id"] == "doc-123"
        assert data["page_number"] == 0
        assert data["mode"] == "basic"
        assert data["status"] == "pending"
    
    def test_get_job_with_result(self, client, job_service):
        """Test getting job with completed result."""
        # Create and complete a job
        job = job_service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        parse_result = ParseResult(
            document_id="doc-123",
            blocks=[Block(type="text", text="Test content")],
            metadata={}
        )
        
        job_service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result=parse_result
        )
        
        # Get job via API
        response = client.get(f"/api/v1/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"] is not None
        assert data["result"]["document_id"] == "doc-123"
        assert len(data["result"]["blocks"]) == 1
    
    def test_get_job_with_error(self, client, job_service):
        """Test getting job with error."""
        # Create and fail a job
        job = job_service.create_job("doc-123", 0, "basic")
        job_id = job.id
        
        job_service.update_job_status(
            job_id,
            JobStatus.FAILED,
            error="Test error message"
        )
        
        # Get job via API
        response = client.get(f"/api/v1/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Test error message"
