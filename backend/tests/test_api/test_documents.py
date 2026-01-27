"""Tests for document API endpoints."""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi import UploadFile

from core.models.document import Document, DocumentStatus


class TestDocumentEndpoints:
    """Test document API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Forge Playground API"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('api.routes.documents.document_service')
    def test_upload_document(self, mock_service, client, sample_file_content):
        """Test document upload."""
        # Mock document creation
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        mock_service.create_from_upload = AsyncMock(return_value=mock_doc)
        
        # Upload file
        files = {"file": ("test.pdf", sample_file_content, "application/pdf")}
        response = client.post("/api/v1/documents", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test-123"
        assert data["filename"] == "test.pdf"
        assert data["file_type"] == "pdf"
    
    def test_upload_document_url_not_implemented(self, client):
        """Test URL upload returns 501."""
        response = client.post(
            "/api/v1/documents/url",
            json={"url": "https://example.com/doc.pdf"}
        )
        assert response.status_code == 501
        assert "not implemented" in response.json()["detail"].lower()
    
    @patch('api.routes.documents.document_service')
    def test_get_document(self, mock_service, client):
        """Test get document."""
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        mock_service.get_by_id.return_value = mock_doc
        
        response = client.get("/api/v1/documents/test-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-123"
        assert data["filename"] == "test.pdf"
    
    @patch('api.routes.documents.document_service')
    def test_get_document_not_found(self, mock_service, client):
        """Test get document returns 404 when not found."""
        mock_service.get_by_id.return_value = None
        
        response = client.get("/api/v1/documents/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch('api.routes.documents.document_service')
    def test_get_page_image(self, mock_service, client):
        """Test get page image."""
        mock_doc = Document(
            id="test-123",
            filename="test.png",
            file_type="png",
            file_path="/tmp/test.png",
            page_count=1,
        )
        mock_service.get_by_id.return_value = mock_doc
        mock_service.get_page_image.return_value = b"image bytes"
        
        response = client.get("/api/v1/documents/test-123/pages/0")
        
        assert response.status_code == 200
        assert response.content == b"image bytes"
        assert response.headers["content-type"] == "image/png"
    
    @patch('api.routes.documents.document_service')
    def test_get_page_image_invalid_page_number(self, mock_service, client):
        """Test get page image with invalid page number."""
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            page_count=1,
        )
        mock_service.get_by_id.return_value = mock_doc
        
        # Page number < 0
        response = client.get("/api/v1/documents/test-123/pages/-1")
        assert response.status_code == 400
        
        # Page number >= page_count
        response = client.get("/api/v1/documents/test-123/pages/1")
        assert response.status_code == 404
    
    def test_delete_document_not_implemented(self, client):
        """Test delete document returns 501."""
        response = client.delete("/api/v1/documents/test-123")
        assert response.status_code == 501
