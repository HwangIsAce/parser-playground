"""Parse result domain model."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Represents a parsed block of content."""
    
    type: str  # 'text', 'table', 'image', 'form_field'
    text: str
    coordinates: Optional[List[Dict[str, float]]] = None  # Upstage style: [{"x": 0.1, "y": 0.2}, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Upstage style additional fields
    page: Optional[int] = None
    element_id: Optional[int] = None
    content: Optional[Dict[str, str]] = None  # {"html": "...", "markdown": "...", "text": "..."}
    
    @property
    def bbox(self) -> Optional[Dict[str, float]]:
        """Calculate bbox from coordinates (backward compatibility).
        
        Returns:
            Dict with keys 'l', 't', 'r', 'b' or None if coordinates not available
        """
        if not self.coordinates or len(self.coordinates) != 4:
            return None
        
        x_coords = [c["x"] for c in self.coordinates]
        y_coords = [c["y"] for c in self.coordinates]
        
        return {
            "l": min(x_coords),
            "t": min(y_coords),
            "r": max(x_coords),
            "b": max(y_coords)
        }


@dataclass
class ParseResult:
    """Result of document parsing."""
    
    document_id: str
    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Upstage style additional fields
    full_content: Optional[Dict[str, str]] = None  # {"html": "...", "markdown": "...", "text": "..."}
    usage: Optional[Dict[str, Any]] = None  # {"pages": 1, ...}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "document_id": self.document_id,
            "blocks": [
                {
                    "type": block.type,
                    "text": block.text,
                    "coordinates": block.coordinates,
                    "bbox": block.bbox,  # Calculated from coordinates (backward compatibility)
                    "metadata": block.metadata,
                    **({"page": block.page} if block.page is not None else {}),
                    **({"element_id": block.element_id} if block.element_id is not None else {}),
                    **({"content": block.content} if block.content else {}),
                }
                for block in self.blocks
            ],
            "metadata": self.metadata,
        }
        
        # Add Upstage style fields if available
        if self.full_content:
            result["content"] = self.full_content
        if self.usage:
            result["usage"] = self.usage
        
        return result
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        # Use full_content if available
        if self.full_content and "html" in self.full_content:
            return self.full_content["html"]
        
        # Otherwise, build from blocks
        html_parts = ["<div class='parse-result'>"]
        for block in self.blocks:
            # Use block.content.html if available
            if block.content and "html" in block.content:
                html_parts.append(block.content["html"])
            elif block.type == "text":
                html_parts.append(f"<p>{block.text}</p>")
            elif block.type == "table":
                html_parts.append(f"<table><tr><td>{block.text}</td></tr></table>")
            else:
                html_parts.append(f"<div class='{block.type}'>{block.text}</div>")
        html_parts.append("</div>")
        return "\n".join(html_parts)
    
    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        # Use full_content if available
        if self.full_content and "markdown" in self.full_content:
            return self.full_content["markdown"]
        
        # Otherwise, build from blocks
        markdown_parts = []
        for block in self.blocks:
            # Use block.content.markdown if available
            if block.content and "markdown" in block.content:
                markdown_parts.append(block.content["markdown"])
            elif block.type == "text":
                markdown_parts.append(block.text)
            elif block.type == "table":
                markdown_parts.append(f"\n{block.text}\n")
            else:
                markdown_parts.append(f"**{block.type}**: {block.text}")
        return "\n\n".join(markdown_parts)
    
    def get_blocks_by_page(self, page: int) -> List[Block]:
        """Get blocks for a specific page.
        
        Args:
            page: Page number
            
        Returns:
            List of blocks on the specified page
        """
        return [b for b in self.blocks if b.page == page]
    
    def get_blocks_by_type(self, block_type: str) -> List[Block]:
        """Get blocks by type.
        
        Args:
            block_type: Block type ('text', 'table', etc.)
            
        Returns:
            List of blocks with the specified type
        """
        return [b for b in self.blocks if b.type == block_type]
    
    def get_tables(self) -> List[Block]:
        """Get all table blocks.
        
        Returns:
            List of table blocks
        """
        return self.get_blocks_by_type("table")
