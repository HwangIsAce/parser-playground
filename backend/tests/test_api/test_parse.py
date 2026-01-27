"""Tests for parse API endpoints."""
import pytest
from unittest.mock import patch, Mock

from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult, Block


class TestParseEndpoints:
    """Test parse API endpoints."""
    
    @patch('api.routes.parse.document_service')
    @patch('api.routes.parse.parser_service')
    def test_parse_document(self, mock_parser_service, mock_doc_service, client):
        """Test parse document."""
        # Mock document
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            page_count=1,
        )
        mock_doc_service.get_by_id.return_value = mock_doc
        
        # Mock parse result
        mock_result = ParseResult(
            document_id="test-123",
            blocks=[Block(type="text", text="Parsed content")],
            metadata={"parser": "docling"},
        )
        mock_parser_service.parse_document.return_value = mock_result
        
        response = client.post(
            "/api/v1/documents/test-123/pages/0/parse",
            json={"mode": "basic"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == "test-123"
        assert len(data["blocks"]) == 1
        assert data["blocks"][0]["type"] == "text"
    
    @patch('api.routes.parse.document_service')
    @patch('api.routes.parse.parser_service')
    def test_parse_document_with_mode(self, mock_parser_service, mock_doc_service, client):
        """Test parse document with specified mode."""
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            page_count=1,
        )
        mock_doc_service.get_by_id.return_value = mock_doc
        
        mock_result = ParseResult(
            document_id="test-123",
            blocks=[],
        )
        mock_parser_service.parse_document.return_value = mock_result
        
        response = client.post(
            "/api/v1/documents/test-123/pages/0/parse",
            json={"mode": "enhance"}
        )
        
        assert response.status_code == 200
        mock_parser_service.parse_document.assert_called_once_with(
            mock_doc,
            mode="enhance"
        )
    
    @patch('api.routes.parse.document_service')
    def test_parse_document_not_found(self, mock_doc_service, client):
        """Test parse document returns 404 when document not found."""
        mock_doc_service.get_by_id.return_value = None
        
        response = client.post(
            "/api/v1/documents/nonexistent/pages/0/parse",
            json={}
        )
        
        assert response.status_code == 404
    
    @patch('api.routes.parse.document_service')
    def test_parse_document_invalid_page_number(self, mock_doc_service, client):
        """Test parse document with invalid page number."""
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            page_count=1,
        )
        mock_doc_service.get_by_id.return_value = mock_doc
        
        # Page number < 0
        response = client.post(
            "/api/v1/documents/test-123/pages/-1/parse",
            json={}
        )
        assert response.status_code == 400
        
        # Page number >= page_count
        response = client.post(
            "/api/v1/documents/test-123/pages/1/parse",
            json={}
        )
        assert response.status_code == 404
    
    @patch('api.routes.parse.parser_service')
    def test_list_parsers(self, mock_parser_service, client):
        """Test list parsers."""
        mock_parser_service.get_available_parsers.return_value = ["docling", "chandra", "unstructured"]
        mock_parser_service.get_available_modes.return_value = ["basic", "enhance"]
        
        response = client.get("/api/v1/parsers")
        
        assert response.status_code == 200
        data = response.json()
        assert "parsers" in data
        assert "modes" in data
        assert "mode_mapping" in data
        assert "basic" in data["modes"]
        assert "enhance" in data["modes"]
    
    @patch('api.routes.parse.document_service')
    def test_get_parse_result_not_implemented(self, mock_doc_service, client):
        """Test get parse result returns 501."""
        mock_doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            page_count=1,
        )
        mock_doc_service.get_by_id.return_value = mock_doc
        
        response = client.get("/api/v1/documents/test-123/pages/0/parse/result")
        
        assert response.status_code == 501
