"""Parse result domain model."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Represents a parsed block of content."""
    
    type: str  # 'text', 'table', 'image', 'form_field'
    text: str
    bbox: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of document parsing."""
    
    document_id: str
    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "blocks": [
                {
                    "type": block.type,
                    "text": block.text,
                    "bbox": block.bbox,
                    "metadata": block.metadata,
                }
                for block in self.blocks
            ],
            "metadata": self.metadata,
        }
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        html_parts = ["<div class='parse-result'>"]
        for block in self.blocks:
            if block.type == "text":
                html_parts.append(f"<p>{block.text}</p>")
            elif block.type == "table":
                html_parts.append(f"<table><tr><td>{block.text}</td></tr></table>")
            else:
                html_parts.append(f"<div class='{block.type}'>{block.text}</div>")
        html_parts.append("</div>")
        return "\n".join(html_parts)
    
    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        markdown_parts = []
        for block in self.blocks:
            if block.type == "text":
                markdown_parts.append(block.text)
            elif block.type == "table":
                markdown_parts.append(f"\n{block.text}\n")
            else:
                markdown_parts.append(f"**{block.type}**: {block.text}")
        return "\n\n".join(markdown_parts)
