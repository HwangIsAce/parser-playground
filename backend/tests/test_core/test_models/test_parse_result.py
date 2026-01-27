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
        assert block.coordinates is None
        assert block.bbox is None
        assert block.metadata == {}
        assert block.page is None
        assert block.element_id is None
        assert block.content is None
    
    def test_create_block_with_coordinates(self):
        """Test block creation with coordinates."""
        coordinates = [
            {"x": 0.1, "y": 0.2},
            {"x": 0.3, "y": 0.2},
            {"x": 0.3, "y": 0.4},
            {"x": 0.1, "y": 0.4}
        ]
        block = Block(
            type="text",
            text="Sample text",
            coordinates=coordinates,
        )
        
        assert block.coordinates == coordinates
        # Test bbox property (calculated from coordinates)
        assert block.bbox is not None
        assert block.bbox["l"] == 0.1
        assert block.bbox["t"] == 0.2
        assert block.bbox["r"] == 0.3
        assert block.bbox["b"] == 0.4
    
    def test_block_bbox_property(self):
        """Test bbox property calculation from coordinates."""
        # Test with coordinates
        coordinates = [
            {"x": 0.1, "y": 0.2},
            {"x": 0.5, "y": 0.2},
            {"x": 0.5, "y": 0.6},
            {"x": 0.1, "y": 0.6}
        ]
        block = Block(type="text", text="Test", coordinates=coordinates)
        bbox = block.bbox
        
        assert bbox is not None
        assert bbox["l"] == 0.1
        assert bbox["t"] == 0.2
        assert bbox["r"] == 0.5
        assert bbox["b"] == 0.6
        
        # Test without coordinates
        block_no_coords = Block(type="text", text="Test")
        assert block_no_coords.bbox is None
    
    def test_create_block_with_metadata(self):
        """Test block creation with metadata."""
        metadata = {"key": "value", "parser": "unstructured"}
        block = Block(
            type="text",
            text="Sample text",
            metadata=metadata,
        )
        
        assert block.metadata == metadata
    
    def test_create_block_with_upstage_fields(self):
        """Test block creation with Upstage style fields."""
        coordinates = [
            {"x": 0.1, "y": 0.2},
            {"x": 0.3, "y": 0.2},
            {"x": 0.3, "y": 0.4},
            {"x": 0.1, "y": 0.4}
        ]
        content = {
            "html": "<p>Sample text</p>",
            "markdown": "Sample text",
            "text": "Sample text"
        }
        
        block = Block(
            type="text",
            text="Sample text",
            coordinates=coordinates,
            page=1,
            element_id=0,
            content=content,
            metadata={"parser": "docling"}
        )
        
        assert block.page == 1
        assert block.element_id == 0
        assert block.content == content
        assert block.coordinates == coordinates


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
        coordinates = [
            {"x": 0.0, "y": 0.0},
            {"x": 1.0, "y": 0.0},
            {"x": 1.0, "y": 0.5},
            {"x": 0.0, "y": 0.5}
        ]
        blocks = [
            Block(
                type="text",
                text="Sample text",
                coordinates=coordinates,
                page=1,
                element_id=0,
                metadata={"key": "value"},
            ),
            Block(
                type="table",
                text="Table content",
                page=1,
                element_id=1,
            ),
        ]
        result = ParseResult(
            document_id="doc-123",
            blocks=blocks,
            full_content={"html": "<div>...</div>", "markdown": "...", "text": "..."},
            usage={"pages": 1},
            metadata={"parser": "unstructured"},
        )
        
        dict_result = result.to_dict()
        
        assert dict_result["document_id"] == "doc-123"
        assert len(dict_result["blocks"]) == 2
        assert dict_result["blocks"][0]["type"] == "text"
        assert dict_result["blocks"][0]["text"] == "Sample text"
        assert dict_result["blocks"][0]["coordinates"] == coordinates
        assert dict_result["blocks"][0]["bbox"] is not None  # Calculated from coordinates
        assert dict_result["blocks"][0]["page"] == 1
        assert dict_result["blocks"][0]["element_id"] == 0
        assert dict_result["blocks"][0]["metadata"] == {"key": "value"}
        assert dict_result["blocks"][1]["type"] == "table"
        assert dict_result["content"] == {"html": "<div>...</div>", "markdown": "...", "text": "..."}
        assert dict_result["usage"] == {"pages": 1}
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
    
    def test_get_blocks_by_page(self):
        """Test get_blocks_by_page() method."""
        blocks = [
            Block(type="text", text="Page 1", page=1),
            Block(type="text", text="Page 2", page=2),
            Block(type="text", text="Page 1 again", page=1),
        ]
        result = ParseResult(document_id="doc-123", blocks=blocks)
        
        page_1_blocks = result.get_blocks_by_page(1)
        assert len(page_1_blocks) == 2
        assert all(b.page == 1 for b in page_1_blocks)
        
        page_2_blocks = result.get_blocks_by_page(2)
        assert len(page_2_blocks) == 1
        assert page_2_blocks[0].page == 2
    
    def test_get_blocks_by_type(self):
        """Test get_blocks_by_type() method."""
        blocks = [
            Block(type="text", text="Text 1"),
            Block(type="table", text="Table 1"),
            Block(type="text", text="Text 2"),
        ]
        result = ParseResult(document_id="doc-123", blocks=blocks)
        
        text_blocks = result.get_blocks_by_type("text")
        assert len(text_blocks) == 2
        
        table_blocks = result.get_blocks_by_type("table")
        assert len(table_blocks) == 1
    
    def test_get_tables(self):
        """Test get_tables() method."""
        blocks = [
            Block(type="text", text="Text"),
            Block(type="table", text="Table 1"),
            Block(type="table", text="Table 2"),
        ]
        result = ParseResult(document_id="doc-123", blocks=blocks)
        
        tables = result.get_tables()
        assert len(tables) == 2
        assert all(t.type == "table" for t in tables)
    
    def test_to_html_with_full_content(self):
        """Test to_html() with full_content."""
        result = ParseResult(
            document_id="doc-123",
            blocks=[],
            full_content={"html": "<div>Full HTML</div>"}
        )
        
        html = result.to_html()
        assert html == "<div>Full HTML</div>"
    
    def test_to_markdown_with_full_content(self):
        """Test to_markdown() with full_content."""
        result = ParseResult(
            document_id="doc-123",
            blocks=[],
            full_content={"markdown": "# Full Markdown"}
        )
        
        markdown = result.to_markdown()
        assert markdown == "# Full Markdown"
