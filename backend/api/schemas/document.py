"""Document API schemas."""
from datetime import datetime
from pydantic import BaseModel, Field

from core.models.document import Document, DocumentStatus


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
    
    @classmethod
    def from_domain(cls, document: Document) -> "DocumentResponse":
        """Create response from domain model.
        
        Args:
            document: Document domain model
            
        Returns:
            DocumentResponse instance
        """
        return cls(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            page_count=document.page_count,
            status=document.status,
            created_at=document.created_at,
        )


class DocumentCreate(BaseModel):
    """Document creation schema (for URL upload)."""
    
    url: str = Field(..., description="URL of the document to download")
