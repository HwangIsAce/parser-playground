"""Tests for RemoteChandraParser."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from infrastructure.parsers.remote_chandra_parser import RemoteChandraParser
from infrastructure.clients.parser_api_client import ParserAPIError
from core.models.document import Document, DocumentStatus


class TestRemoteChandraParser:
    """Test RemoteChandraParser."""
    
    def test_get_name(self):
        """Test get_name returns 'chandra-remote'."""
        with patch.object(RemoteChandraParser, '__init__', lambda self: None):
            parser = RemoteChandraParser()
            parser.client = Mock()
            parser.storage = Mock()
            assert parser.get_name() == "chandra-remote"
    
    def test_get_supported_formats(self):
        """Test get_supported_formats returns correct formats."""
        with patch.object(RemoteChandraParser, '__init__', lambda self: None):
            parser = RemoteChandraParser()
            parser.client = Mock()
            parser.storage = Mock()
            formats = parser.get_supported_formats()
            
            assert isinstance(formats, list)
            assert "pdf" in formats
            assert "png" in formats
            assert "jpg" in formats
    
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_prepare_file_content_image(self, mock_settings, mock_client_class, mock_storage_class):
        """Test file content preparation for image files."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage = Mock()
        mock_storage.load.return_value = b"image content"
        mock_storage_class.return_value = mock_storage
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.png",
            file_type="png",
            file_path="/path/to/test.png",
            status=DocumentStatus.COMPLETED,
        )
        
        content, filename = parser._prepare_file_content(doc)
        
        assert content == b"image content"
        assert filename == "test.png"
        mock_storage.load.assert_called_once_with("/path/to/test.png")
    
    @patch('infrastructure.parsers.remote_chandra_parser.convert_from_path')
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_prepare_file_content_pdf(self, mock_settings, mock_client_class, mock_storage_class, mock_convert):
        """Test file content preparation for PDF files."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage_class.return_value = Mock()
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock PDF to image conversion
        mock_image = Image.new('RGB', (100, 100), color='white')
        mock_convert.return_value = [mock_image]
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        content, filename = parser._prepare_file_content(doc)
        
        assert isinstance(content, bytes)
        assert filename == "test.png"
        mock_convert.assert_called_once_with("/path/to/test.pdf")
    
    @patch('infrastructure.parsers.remote_chandra_parser.convert_from_path')
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_prepare_file_content_pdf_no_pages(self, mock_settings, mock_client_class, mock_storage_class, mock_convert):
        """Test error when PDF has no pages."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage_class.return_value = Mock()
        mock_client_class.return_value = Mock()
        
        # Mock empty PDF
        mock_convert.return_value = []
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        with pytest.raises(ValueError, match="no pages found"):
            parser._prepare_file_content(doc)
    
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_do_parse_success_with_json_blocks(self, mock_settings, mock_client_class, mock_storage_class):
        """Test successful parsing with JSON blocks."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage = Mock()
        mock_storage.load.return_value = b"image content"
        mock_storage_class.return_value = mock_storage
        
        mock_client = Mock()
        mock_client.process_ocr.return_value = {
            "id": "ocr-123",
            "text": "OCR text",
            "markdown": "# Title\nText",
            "html": "<h1>Title</h1>",
            "json": {
                "blocks": [
                    {
                        "type": "text",
                        "text": "Block 1",
                        "html": "<p>Block 1</p>",
                        "markdown": "Block 1"
                    },
                    {
                        "type": "table",
                        "text": "Table content",
                        "html": "<table>...</table>",
                        "markdown": "Table"
                    }
                ]
            },
            "metadata": {"page_count": 1}
        }
        mock_client_class.return_value = mock_client
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.png",
            file_type="png",
            file_path="/path/to/test.png",
            status=DocumentStatus.COMPLETED,
        )
        
        result = parser._do_parse(doc)
        
        assert result.document_id == "test-doc"
        assert len(result.blocks) == 2
        assert result.blocks[0].type == "text"
        assert result.blocks[1].type == "table"
        assert result.metadata["parser"] == "chandra-remote"
        assert result.full_content["text"] == "OCR text"
        
        mock_client.process_ocr.assert_called_once_with(
            "test.png",
            b"image content",
            prompt_type="ocr_layout",
            output_format="markdown"
        )
    
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_do_parse_success_with_html_tables(self, mock_settings, mock_client_class, mock_storage_class):
        """Test successful parsing with HTML tables."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage = Mock()
        mock_storage.load.return_value = b"image content"
        mock_storage_class.return_value = mock_storage
        
        mock_client = Mock()
        mock_client.process_ocr.return_value = {
            "id": "ocr-123",
            "text": "Text content",
            "markdown": "Text content",
            "html": "<table><tr><td>Table</td></tr></table><p>Text</p>",
            "json": {},
            "metadata": {"page_count": 1}
        }
        mock_client_class.return_value = mock_client
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.png",
            file_type="png",
            file_path="/path/to/test.png",
            status=DocumentStatus.COMPLETED,
        )
        
        result = parser._do_parse(doc)
        
        assert result.document_id == "test-doc"
        # Should have table block and text block
        assert len(result.blocks) >= 1
        table_blocks = [b for b in result.blocks if b.type == "table"]
        assert len(table_blocks) > 0
    
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_do_parse_api_error(self, mock_settings, mock_client_class, mock_storage_class):
        """Test error handling when API call fails."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage = Mock()
        mock_storage.load.return_value = b"image content"
        mock_storage_class.return_value = mock_storage
        
        mock_client = Mock()
        mock_client.process_ocr.side_effect = ParserAPIError("API error")
        mock_client_class.return_value = mock_client
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.png",
            file_type="png",
            file_path="/path/to/test.png",
            status=DocumentStatus.COMPLETED,
        )
        
        with pytest.raises(ValueError, match="Failed to call remote Chandra API"):
            parser._do_parse(doc)
    
    @patch('infrastructure.parsers.remote_chandra_parser.FileStorage')
    @patch('infrastructure.parsers.remote_chandra_parser.ParserAPIClient')
    @patch('infrastructure.parsers.remote_chandra_parser.settings')
    def test_prepare_file_content_pdf_import_error(self, mock_settings, mock_client_class, mock_storage_class):
        """Test error when pdf2image is not installed."""
        mock_settings.PARSER_API_BASE_URL = "http://localhost:8000"
        mock_settings.PARSER_API_TIMEOUT = 360
        mock_settings.PARSER_API_RETRY_COUNT = 3
        
        mock_storage_class.return_value = Mock()
        mock_client_class.return_value = Mock()
        
        parser = RemoteChandraParser()
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            file_type="pdf",
            file_path="/path/to/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        with patch.dict('sys.modules', {'pdf2image': None}):
            with pytest.raises(ValueError, match="pdf2image is not installed"):
                parser._prepare_file_content(doc)
