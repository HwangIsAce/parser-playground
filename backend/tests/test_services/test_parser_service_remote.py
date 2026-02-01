"""Tests for ParserService with remote parser mode."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from application.services.parser_service import ParserService
from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult, Block


class TestParserServiceRemote:
    """Test ParserService with remote parser mode."""
    
    @patch('application.services.parser_service.settings')
    def test_init_with_remote_enabled(self, mock_settings):
        """Test initialization with remote API enabled."""
        mock_settings.PARSER_API_ENABLED = True
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        service = ParserService()
        
        assert service.mode_mapping["basic"] == "docling-remote"
        assert service.mode_mapping["enhance"] == "chandra-remote"
    
    @patch('application.services.parser_service.settings')
    def test_init_with_remote_disabled(self, mock_settings):
        """Test initialization with remote API disabled."""
        mock_settings.PARSER_API_ENABLED = False
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        service = ParserService()
        
        assert service.mode_mapping["basic"] == "docling"
        assert service.mode_mapping["enhance"] == "chandra"
    
    @patch('application.services.parser_service.ParserFactory')
    @patch('application.services.parser_service.settings')
    def test_parse_document_with_remote_mode(self, mock_settings, mock_factory):
        """Test parse_document uses remote parser when enabled."""
        mock_settings.PARSER_API_ENABLED = True
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        # Mock remote parser
        mock_remote_parser = Mock()
        mock_remote_parser.parse.return_value = ParseResult(
            document_id="test",
            blocks=[Block(type="text", text="Parsed content")],
            metadata={"parser": "docling-remote"}
        )
        
        mock_factory.create.return_value = mock_remote_parser
        mock_factory.list_available.return_value = ["docling-remote", "chandra-remote"]
        
        service = ParserService()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        result = service.parse_document(doc, mode="basic")
        
        assert isinstance(result, ParseResult)
        assert result.document_id == "test"
        # Verify remote parser was created
        mock_factory.create.assert_called_with("docling-remote", config={})
        mock_remote_parser.parse.assert_called_once_with(doc)
    
    @patch('application.services.parser_service.ParserFactory')
    @patch('application.services.parser_service.settings')
    def test_parse_document_with_local_mode(self, mock_settings, mock_factory):
        """Test parse_document uses local parser when remote disabled."""
        mock_settings.PARSER_API_ENABLED = False
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        # Mock local parser
        mock_local_parser = Mock()
        mock_local_parser.parse.return_value = ParseResult(
            document_id="test",
            blocks=[Block(type="text", text="Parsed content")],
            metadata={"parser": "docling"}
        )
        
        mock_factory.create.return_value = mock_local_parser
        mock_factory.list_available.return_value = ["docling", "chandra"]
        
        service = ParserService()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        result = service.parse_document(doc, mode="basic")
        
        assert isinstance(result, ParseResult)
        # Verify local parser was created
        mock_factory.create.assert_called_with("docling", config={})
        mock_local_parser.parse.assert_called_once_with(doc)
    
    @patch('application.services.parser_service.ParserFactory')
    @patch('application.services.parser_service.settings')
    def test_get_parser_caches_remote_parser(self, mock_settings, mock_factory):
        """Test that remote parser instances are cached."""
        mock_settings.PARSER_API_ENABLED = True
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        mock_parser = Mock()
        mock_factory.create.return_value = mock_parser
        
        service = ParserService()
        
        # First call
        parser1 = service._get_parser("docling-remote")
        
        # Second call should use cache
        parser2 = service._get_parser("docling-remote")
        
        assert parser1 is parser2
        # Should only create once
        assert mock_factory.create.call_count == 1
    
    @patch('application.services.parser_service.ParserFactory')
    @patch('application.services.parser_service.settings')
    def test_mode_mapping_switches_based_on_config(self, mock_settings, mock_factory):
        """Test that mode_mapping changes when config changes."""
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        
        # First with remote disabled
        mock_settings.PARSER_API_ENABLED = False
        service1 = ParserService()
        assert service1.mode_mapping["basic"] == "docling"
        
        # Then with remote enabled
        mock_settings.PARSER_API_ENABLED = True
        service2 = ParserService()
        assert service2.mode_mapping["basic"] == "docling-remote"
    
    @patch('application.services.parser_service.ParserFactory')
    @patch('application.services.parser_service.settings')
    def test_get_available_modes_unchanged(self, mock_settings, mock_factory):
        """Test that get_available_modes returns same modes regardless of remote setting."""
        mock_settings.DEFAULT_PARSE_MODE = "basic"
        mock_settings.PARSER_CONFIGS = {}
        mock_factory.list_available.return_value = []
        
        # With remote disabled
        mock_settings.PARSER_API_ENABLED = False
        service1 = ParserService()
        modes1 = service1.get_available_modes()
        
        # With remote enabled
        mock_settings.PARSER_API_ENABLED = True
        service2 = ParserService()
        modes2 = service2.get_available_modes()
        
        # Modes should be the same
        assert set(modes1) == set(modes2)
        assert "basic" in modes1
        assert "enhance" in modes1
