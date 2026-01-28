"""Tests for Parse API with async job queue."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from api.app import create_app
from application.services.document_service import DocumentService
from core.models.document import Document, DocumentStatus
from core.models.job import JobStatus


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_document():
    """Create sample document."""
    from datetime import datetime
    
    return Document(
        id="test-doc-123",
        filename="test.pdf",
        file_type="pdf",
        file_path="/tmp/test.pdf",
        page_count=1,
        status=DocumentStatus.COMPLETED,
        created_at=datetime.now(),
        metadata={}
    )


class TestParseAPIAsync:
    """Test Parse API with async job queue."""
    
    @patch('api.routes.parse.document_service')
    @patch('api.routes.parse.default_queue')
    def test_parse_document_creates_job(self, mock_queue, mock_doc_service, client, sample_document):
        """Test that parse request creates a job and queues it."""
        # Setup mocks
        mock_doc_service.get_by_id.return_value = sample_document
        mock_enqueue = MagicMock()
        mock_queue.enqueue = mock_enqueue
        
        # Make request
        response = client.post(
            "/api/v1/documents/test-doc-123/pages/0/parse",
            json={"mode": "basic"}
        )
        
        # Assertions
        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "id" in data  # job_id
        assert data["document_id"] == "test-doc-123"
        assert data["page_number"] == 0
        assert data["mode"] == "basic"
        assert data["status"] == "queued"
        
        # Verify task was queued
        assert mock_enqueue.called
        call_args = mock_enqueue.call_args
        assert call_args[0][0].__name__ == "parse_document_task"  # Function name
    
    @patch('api.routes.parse.document_service')
    def test_parse_document_not_found(self, mock_doc_service, client):
        """Test parse request with nonexistent document."""
        mock_doc_service.get_by_id.return_value = None
        
        response = client.post(
            "/api/v1/documents/nonexistent/pages/0/parse",
            json={"mode": "basic"}
        )
        
        assert response.status_code == 404
    
    @patch('api.routes.parse.document_service')
    def test_parse_document_invalid_mode(self, mock_doc_service, client, sample_document):
        """Test parse request with invalid mode."""
        mock_doc_service.get_by_id.return_value = sample_document
        
        response = client.post(
            "/api/v1/documents/test-doc-123/pages/0/parse",
            json={"mode": "invalid"}
        )
        
        assert response.status_code == 400
        assert "invalid mode" in response.json()["detail"].lower()
    
    @patch('api.routes.parse.document_service')
    def test_parse_document_invalid_page(self, mock_doc_service, client, sample_document):
        """Test parse request with invalid page number."""
        mock_doc_service.get_by_id.return_value = sample_document
        
        response = client.post(
            "/api/v1/documents/test-doc-123/pages/10/parse",
            json={"mode": "basic"}
        )
        
        assert response.status_code == 404
