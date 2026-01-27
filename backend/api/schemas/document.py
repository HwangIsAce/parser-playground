"""Document API schemas."""
from datetime import datetime
from pydantic import BaseModel, Field

from core.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    """Document response schema."""
    
    id: str
    filename: str
    file_type: str
    page_count: int
    status: DocumentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    """Document creation schema (for URL upload)."""
    
    url: str = Field(..., description="URL of the document to download")
