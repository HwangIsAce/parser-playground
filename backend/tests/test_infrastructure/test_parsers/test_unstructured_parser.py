"""Tests for UnstructuredParser."""
import pytest

from infrastructure.parsers.unstructured_parser import UnstructuredParser
from core.models.document import Document, DocumentStatus


class TestUnstructuredParser:
    """Test UnstructuredParser."""
    
    def test_get_name(self):
        """Test get_name returns 'unstructured'."""
        parser = UnstructuredParser()
        assert parser.get_name() == "unstructured"
    
    def test_get_supported_formats(self):
        """Test get_supported_formats returns correct formats."""
        parser = UnstructuredParser()
        formats = parser.get_supported_formats()
        
        assert isinstance(formats, list)
        assert "pdf" in formats
        assert "png" in formats
        assert "docx" in formats
        assert "xlsx" in formats
    
    def test_parse_creates_result(self):
        """Test _do_parse creates ParseResult."""
        parser = UnstructuredParser()
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
            status=DocumentStatus.COMPLETED,
        )
        
        result = parser._do_parse(doc)
        
        assert result.document_id == "test"
        assert len(result.blocks) > 0
        assert result.blocks[0].type == "text"
        assert "test.pdf" in result.blocks[0].text
        assert result.metadata["parser"] == "unstructured"
        assert result.metadata["file_type"] == "pdf"
    
    def test_parse_with_different_file_types(self):
        """Test parse with different file types."""
        parser = UnstructuredParser()
        
        for file_type in ["pdf", "png", "docx"]:
            doc = Document(
                id=f"test-{file_type}",
                filename=f"test.{file_type}",
                file_type=file_type,
                file_path=f"/tmp/test.{file_type}",
            )
            result = parser._do_parse(doc)
            assert result.document_id == f"test-{file_type}"
            assert result.metadata["file_type"] == file_type
