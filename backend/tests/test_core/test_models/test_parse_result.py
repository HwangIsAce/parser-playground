"""Tests for ParseResult domain model."""
import pytest

from core.models.parse_result import ParseResult, Block


class TestBlock:
    """Test Block model."""
    
    def test_create_block(self):
        """Test block creation."""
        block = Block(
            type="text",
            text="Sample text",
        )
        
        assert block.type == "text"
        assert block.text == "Sample text"
        assert block.bbox is None
        assert block.metadata == {}
    
    def test_create_block_with_bbox(self):
        """Test block creation with bounding box."""
        bbox = {"x": 10, "y": 20, "width": 100, "height": 50}
        block = Block(
            type="text",
            text="Sample text",
            bbox=bbox,
        )
        
        assert block.bbox == bbox
    
    def test_create_block_with_metadata(self):
        """Test block creation with metadata."""
        metadata = {"key": "value", "parser": "unstructured"}
        block = Block(
            type="text",
            text="Sample text",
            metadata=metadata,
        )
        
        assert block.metadata == metadata


class TestParseResult:
    """Test ParseResult model."""
    
    def test_create_parse_result(self):
        """Test parse result creation."""
        result = ParseResult(document_id="doc-123")
        
        assert result.document_id == "doc-123"
        assert result.blocks == []
        assert result.metadata == {}
    
    def test_create_parse_result_with_blocks(self):
        """Test parse result creation with blocks."""
        blocks = [
            Block(type="text", text="Text 1"),
            Block(type="table", text="Table 1"),
        ]
        result = ParseResult(
            document_id="doc-123",
            blocks=blocks,
        )
        
        assert len(result.blocks) == 2
        assert result.blocks[0].type == "text"
        assert result.blocks[1].type == "table"
    
    def test_create_parse_result_with_metadata(self):
        """Test parse result creation with metadata."""
        metadata = {"parser": "unstructured", "file_type": "pdf"}
        result = ParseResult(
            document_id="doc-123",
            metadata=metadata,
        )
        
        assert result.metadata == metadata
    
    def test_to_dict(self):
        """Test to_dict() method."""
        blocks = [
            Block(
                type="text",
                text="Sample text",
                bbox={"x": 0, "y": 0, "width": 100, "height": 50},
                metadata={"key": "value"},
            ),
            Block(
                type="table",
                text="Table content",
            ),
        ]
        result = ParseResult(
            document_id="doc-123",
            blocks=blocks,
            metadata={"parser": "unstructured"},
        )
        
        dict_result = result.to_dict()
        
        assert dict_result["document_id"] == "doc-123"
        assert len(dict_result["blocks"]) == 2
        assert dict_result["blocks"][0]["type"] == "text"
        assert dict_result["blocks"][0]["text"] == "Sample text"
        assert dict_result["blocks"][0]["bbox"] == {"x": 0, "y": 0, "width": 100, "height": 50}
        assert dict_result["blocks"][0]["metadata"] == {"key": "value"}
        assert dict_result["blocks"][1]["type"] == "table"
        assert dict_result["metadata"] == {"parser": "unstructured"}
    
    def test_to_dict_empty_blocks(self):
        """Test to_dict() with empty blocks."""
        result = ParseResult(document_id="doc-123")
        dict_result = result.to_dict()
        
        assert dict_result["document_id"] == "doc-123"
        assert dict_result["blocks"] == []
        assert dict_result["metadata"] == {}
    
    def test_to_html(self):
        """Test to_html() method."""
        blocks = [
            Block(type="text", text="Text content"),
            Block(type="table", text="Table content"),
            Block(type="image", text="Image content"),
        ]
        result = ParseResult(
            document_id="doc-123",
            blocks=blocks,
        )
        
        html = result.to_html()
        
        assert "<div class='parse-result'>" in html
        assert "<p>Text content</p>" in html
        assert "<table><tr><td>Table content</td></tr></table>" in html
        assert "<div class='image'>Image content</div>" in html
        assert "</div>" in html
    
    def test_to_html_empty_blocks(self):
        """Test to_html() with empty blocks."""
        result = ParseResult(document_id="doc-123")
        html = result.to_html()
        
        assert "<div class='parse-result'>" in html
        assert "</div>" in html
    
    def test_to_markdown(self):
        """Test to_markdown() method."""
        blocks = [
            Block(type="text", text="Text content"),
            Block(type="table", text="Table content"),
            Block(type="image", text="Image content"),
        ]
        result = ParseResult(
            document_id="doc-123",
            blocks=blocks,
        )
        
        markdown = result.to_markdown()
        
        assert "Text content" in markdown
        assert "\nTable content\n" in markdown
        assert "**image**: Image content" in markdown
    
    def test_to_markdown_empty_blocks(self):
        """Test to_markdown() with empty blocks."""
        result = ParseResult(document_id="doc-123")
        markdown = result.to_markdown()
        
        assert markdown == ""
