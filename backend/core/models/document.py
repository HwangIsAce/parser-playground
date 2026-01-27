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
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        self._validate()
    
    def is_image(self) -> bool:
        """Check if document is an image."""
        image_types = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'tiff']
        return self.file_type.lower() in image_types
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF."""
        return self.file_type.lower() == 'pdf'
    
    def is_supported(self) -> bool:
        """Check if document format is supported."""
        supported = [
            'pdf', 'doc', 'docx', 'odt',  # Documents
            'xls', 'xlsx', 'xlst', 'xlsm', 'ods',  # Spreadsheets
            'ppt', 'pptx', 'odp',  # Presentations
            'html', 'epub',  # Web & Books
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',  # Images
        ]
        return self.file_type.lower() in supported
    
    def _validate(self):
        """Validate document entity."""
        if not self.id:
            raise ValueError("Document ID is required")
        if not self.filename:
            raise ValueError("Document filename is required")
        if not self.file_type:
            raise ValueError("Document file type is required")
