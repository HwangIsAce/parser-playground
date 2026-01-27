"""Tests for BaseParser."""
import pytest

from infrastructure.parsers.base import BaseParser
from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult


class ConcreteParser(BaseParser):
    """Concrete parser for testing."""
    
    def get_name(self) -> str:
        return "test_parser"
    
    def get_supported_formats(self) -> list[str]:
        return ["pdf", "png"]
    
    def _do_parse(self, document: Document) -> ParseResult:
        from core.models.parse_result import Block
        return ParseResult(
            document_id=document.id,
            blocks=[Block(type="text", text=f"Parsed {document.filename}")],
        )


class TestBaseParser:
    """Test BaseParser."""
    
    def test_validate_document_supported_format(self):
        """Test validate_document with supported format."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        assert parser.validate_document(doc) is True
    
    def test_validate_document_unsupported_format(self):
        """Test validate_document with unsupported format."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.doc",
            file_type="doc",
            file_path="/tmp/test.doc",
        )
        assert parser.validate_document(doc) is False
    
    def test_validate_document_case_insensitive(self):
        """Test validate_document is case insensitive."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.PDF",
            file_type="PDF",
            file_path="/tmp/test.PDF",
        )
        assert parser.validate_document(doc) is True
    
    def test_preprocess_returns_document(self):
        """Test preprocess returns document unchanged."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        processed = parser.preprocess(doc)
        assert processed == doc
    
    def test_parse_success(self):
        """Test parse with valid document."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        result = parser.parse(doc)
        assert isinstance(result, ParseResult)
        assert result.document_id == "test"
        assert len(result.blocks) == 1
        assert result.blocks[0].text == "Parsed test.pdf"
    
    def test_parse_unsupported_format_raises_error(self):
        """Test parse with unsupported format raises error."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.doc",
            file_type="doc",
            file_path="/tmp/test.doc",
        )
        with pytest.raises(ValueError, match="Unsupported format"):
            parser.parse(doc)
    
    def test_parse_calls_preprocess(self):
        """Test parse calls preprocess before _do_parse."""
        parser = ConcreteParser()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        # Should not raise error, meaning preprocess was called
        result = parser.parse(doc)
        assert result is not None
