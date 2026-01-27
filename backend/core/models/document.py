"""Document domain model."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentStatus(str, Enum):
    """Document processing status."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """Document entity representing an uploaded document."""
    
    id: str
    filename: str
    file_type: str
    file_path: str
    page_count: int = 1
    status: DocumentStatus = DocumentStatus.UPLOADING
    created_at: datetime = None
    metadata: dict = None
    
    def __post_init__(self):
        """Initialize default values."""
        pass
    
    def is_image(self) -> bool:
        """Check if document is an image."""
        raise NotImplementedError
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF."""
        raise NotImplementedError
    
    def is_supported(self) -> bool:
        """Check if document format is supported."""
        raise NotImplementedError
    
    def _validate(self):
        """Validate document entity."""
        raise NotImplementedError
