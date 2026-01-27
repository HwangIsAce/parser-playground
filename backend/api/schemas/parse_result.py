"""Parse result API schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class BlockResponse(BaseModel):
    """Block response schema."""
    
    type: str
    text: str
    bbox: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = {}


class ParseRequest(BaseModel):
    """Parse request schema."""
    
    parser_name: Optional[str] = None
    strategy: Optional[str] = None
    languages: Optional[List[str]] = None
    render_html: bool = False


class ParseResponse(BaseModel):
    """Parse result response schema."""
    
    document_id: str
    blocks: List[BlockResponse]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True
