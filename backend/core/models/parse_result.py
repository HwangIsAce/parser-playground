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
        raise NotImplementedError
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        raise NotImplementedError
    
    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        raise NotImplementedError
