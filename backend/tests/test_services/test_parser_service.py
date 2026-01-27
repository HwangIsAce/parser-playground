"""Tests for ParserService."""
import pytest
from unittest.mock import Mock, patch

from application.services.parser_service import ParserService
from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult, Block
from core.interfaces.parser_interface import ParserInterface


class MockParser(ParserInterface):
    """Mock parser for testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def get_name(self) -> str:
        return "mock_parser"
    
    def get_supported_formats(self) -> list[str]:
        return ["pdf", "png"]
    
    def parse(self, document) -> ParseResult:
        return ParseResult(
            document_id=document.id,
            blocks=[Block(type="text", text=f"Parsed {document.filename}")],
        )


class TestParserService:
    """Test ParserService."""
    
    def test_init(self):
        """Test initialization."""
        service = ParserService()
        assert service.mode_mapping is not None
        assert "basic" in service.mode_mapping
        assert "enhance" in service.mode_mapping
        assert service._parser_cache == {}
    
    @patch('application.services.parser_service.ParserFactory')
    def test_parse_document_with_default_parser(self, mock_factory):
        """Test parse_document with default mode (basic)."""
        mock_parser = MockParser()
        mock_factory.create.return_value = mock_parser
        mock_factory.list_available.return_value = ["docling", "chandra"]
        
        service = ParserService()
        service._get_parser = lambda name: mock_parser
        
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        result = service.parse_document(doc, mode="basic")
        
        assert isinstance(result, ParseResult)
        assert result.document_id == "test"
        assert len(result.blocks) == 1
    
    @patch('application.services.parser_service.ParserFactory')
    def test_parse_document_with_specified_mode(self, mock_factory):
        """Test parse_document with specified mode."""
        mock_parser = MockParser()
        mock_factory.create.return_value = mock_parser
        
        service = ParserService()
        service._get_parser = lambda name: mock_parser
        
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        result = service.parse_document(doc, mode="enhance")
        
        assert isinstance(result, ParseResult)
    
    @patch('application.services.parser_service.ParserFactory')
    def test_parse_document_raises_value_error_on_parser_error(self, mock_factory):
        """Test parse_document raises ValueError on parser error."""
        mock_parser = Mock(spec=ParserInterface)
        mock_parser.parse = Mock(side_effect=ValueError("Parser error"))
        
        service = ParserService()
        service._get_parser = lambda name: mock_parser
        
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        with pytest.raises(ValueError, match="Failed to parse document"):
            service.parse_document(doc)
    
    @patch('application.services.parser_service.ParserFactory')
    def test_get_available_parsers(self, mock_factory):
        """Test get_available_parsers."""
        mock_factory.list_available.return_value = ["docling", "chandra", "unstructured"]
        
        service = ParserService()
        parsers = service.get_available_parsers()
        
        assert "docling" in parsers or "chandra" in parsers or "unstructured" in parsers
        mock_factory.list_available.assert_called_once()
    
    def test_get_available_modes(self):
        """Test get_available_modes."""
        service = ParserService()
        modes = service.get_available_modes()
        
        assert "basic" in modes
        assert "enhance" in modes
        assert len(modes) == 2
    
    @patch('application.services.parser_service.ParserFactory')
    def test_get_parser_caches_instance(self, mock_factory):
        """Test _get_parser caches parser instances."""
        mock_parser = MockParser()
        mock_factory.create.return_value = mock_parser
        
        service = ParserService()
        
        # First call
        parser1 = service._get_parser("mock_parser")
        
        # Second call should use cache
        parser2 = service._get_parser("mock_parser")
        
        assert parser1 is parser2
        # Should only create once
        assert mock_factory.create.call_count == 1
    
    @patch('application.services.parser_service.ParserFactory')
    def test_get_parser_creates_different_parsers(self, mock_factory):
        """Test _get_parser creates different parsers."""
        def create_parser(name, config=None):
            parser = MockParser(config)
            parser.get_name = lambda: name
            return parser
        
        mock_factory.create.side_effect = create_parser
        
        service = ParserService()
        
        parser1 = service._get_parser("parser1")
        parser2 = service._get_parser("parser2")
        
        assert parser1 is not parser2
        assert parser1.get_name() == "parser1"
        assert parser2.get_name() == "parser2"
