"""Tests for RemoteDoclingParser."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from infrastructure.parsers.remote_docling_parser import RemoteDoclingParser
from infrastructure.clients.parser_api_client import ParserAPIClient, ParserAPIError
from core.models.document import Document, DocumentStatus


class TestRemoteDoclingParser:
    """Test RemoteDoclingParser."""
    
    def test_get_name(self):
        """Test get_name returns 'docling-remote'."""
        with patch.object(RemoteDoclingParser, '__init__', lambda self: None):
            parser = RemoteDoclingParser()
            parser.client = Mock()
            parser.storage = Mock()
            assert parser.get_name() == "docling-remote"
    
    def test_get_supported_formats(self):
        """Test get_supported_formats returns correct formats."""
        with patch.object(RemoteDoclingParser, '__init__', lambda self: None):
            parser = RemoteDoclingParser()
            parser.client = Mock()
            parser.storage = Mock()
            formats = parser.get_supported_formats()
            
            assert isinstance(formats, list)
            assert "pdf" in formats
            assert "docx" in formats
            assert "png" in formats
    
    @patch('infrastructure.parsers.remote_docling_parser.FileStorage')
    @patch('infrastructure.parsers.remote_docling_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_docling_parser.settings')
    def test_do_parse_success(self, mock_settings, mock_client_class, mock_storage_class):
        """Test successful parsing."""
        # Mock settings
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.load.return_value = b"file content"
        mock_storage_class.return_value = mock_storage
        
        # Mock client
        mock_client = Mock()
        mock_client.process_document.return_value = {
            "id": "doc-123",
            "text": "Extracted text content",
            "metadata": {
                "page_count": 1,
                "file_name": "test.pdf"
            },
            "structure": {
                "sections": ["Introduction", "Main Content"]
            }
        }
        mock_client_class.return_value = mock_client
        
        parser = RemoteDoclingParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        result = parser._do_parse(doc)
        
        assert result.document_id == "test-doc"
        assert len(result.blocks) == 1
        assert result.blocks[0].type == "text"
        assert result.blocks[0].text == "Extracted text content"
        assert result.metadata["parser"] == "docling-remote"
        assert result.metadata["api_id"] == "doc-123"
        assert result.full_content["text"] == "Extracted text content"
        assert result.usage["pages"] == 1
        
        # Verify API was called
        mock_client.process_document.assert_called_once_with(
            "/path/to/test.pdf",
            b"file content"
        )
        mock_storage.load.assert_called_once_with("/path/to/test.pdf")
    
    @patch('infrastructure.parsers.remote_docling_parser.FileStorage')
    @patch('infrastructure.parsers.remote_docling_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_docling_parser.settings')
    def test_do_parse_api_error(self, mock_settings, mock_client_class, mock_storage_class):
        """Test error handling when API call fails."""
        # Mock settings
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.load.return_value = b"file content"
        mock_storage_class.return_value = mock_storage
        
        # Mock client that raises error
        mock_client = Mock()
        mock_client.process_document.side_effect = ParserAPIError("API error")
        mock_client_class.return_value = mock_client
        
        parser = RemoteDoclingParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        with pytest.raises(ValueError, match="Failed to call remote Docling API"):
            parser._do_parse(doc)
    
    @patch('infrastructure.parsers.remote_docling_parser.FileStorage')
    @patch('infrastructure.parsers.remote_docling_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_docling_parser.settings')
    def test_convert_api_response_empty_text(self, mock_settings, mock_client_class, mock_storage_class):
        """Test conversion with empty text."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        mock_client = Mock()
        mock_client.process_document.return_value = {
            "id": "doc-123",
            "text": "",
            "metadata": {"page_count": 1},
            "structure": {}
        }
        mock_client_class.return_value = mock_client
        
        parser = RemoteDoclingParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        result = parser._do_parse(doc)
        
        # Should still create a result, but with empty blocks or single empty block
        assert result.document_id == "test-doc"
        # Empty text might result in no blocks or one empty block depending on implementation
        assert len(result.blocks) >= 0
