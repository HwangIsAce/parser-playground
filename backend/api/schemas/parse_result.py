"""Parse result API schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.models.parse_result import ParseResult


class BlockResponse(BaseModel):
    """Block response schema."""
    
    type: str
    text: str
    coordinates: Optional[List[Dict[str, float]]] = None
    bbox: Optional[Dict[str, float]] = None  # Calculated from coordinates (backward compatibility)
    metadata: Dict[str, Any] = {}
    
    # Upstage style additional fields
    page: Optional[int] = None
    element_id: Optional[int] = None
    content: Optional[Dict[str, str]] = None


class ParseRequest(BaseModel):
    """Parse request schema."""
    
    mode: str = Field(
        default="basic",
        description="Parse mode: 'basic' (Docling) or 'enhance' (Chandra)"
    )
    strategy: Optional[str] = None
    languages: Optional[List[str]] = None
    render_html: bool = False


class ParseResponse(BaseModel):
    """Parse result response schema."""
    
    document_id: str
    blocks: List[BlockResponse]
    metadata: Dict[str, Any]
    
    # Upstage style additional fields
    content: Optional[Dict[str, str]] = None
    usage: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_domain(cls, parse_result: ParseResult) -> "ParseResponse":
        """Create response from domain model.
        
        Args:
            parse_result: ParseResult domain model
            
        Returns:
            ParseResponse instance
        """
        return cls(
            document_id=parse_result.document_id,
            blocks=[
                BlockResponse(
                    type=block.type,
                    text=block.text,
                    coordinates=block.coordinates,
                    bbox=block.bbox,  # Calculated from coordinates
                    metadata=block.metadata,
                    page=block.page,
                    element_id=block.element_id,
                    content=block.content,
                )
                for block in parse_result.blocks
            ],
            metadata=parse_result.metadata,
            content=parse_result.full_content,
            usage=parse_result.usage,
        )
