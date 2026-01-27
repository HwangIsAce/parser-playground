"""Document service for document management."""
from typing import Optional

from fastapi import UploadFile

from core.models.document import Document
from core.interfaces.storage_interface import StorageInterface


class DocumentService:
    """Service for document management operations."""
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        """Initialize document service.
        
        Args:
            storage: Storage implementation (defaults to FileStorage)
        """
        pass
    
    async def create_from_upload(self, upload_file: UploadFile) -> Document:
        """Create document from uploaded file.
        
        Args:
            upload_file: FastAPI UploadFile object
            
        Returns:
            Document entity
        """
        raise NotImplementedError
    
    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document entity or None if not found
        """
        raise NotImplementedError
    
    def get_page_image(self, document: Document, page_number: int) -> Optional[bytes]:
        """Get page image for document viewer.
        
        Args:
            document: Document entity
            page_number: Page number (0-indexed)
            
        Returns:
            Image bytes or None if not available
        """
        raise NotImplementedError
    
    def _get_file_type(self, filename: str) -> str:
        """Extract file type from filename.
        
        Args:
            filename: Filename with extension
            
        Returns:
            File extension without dot
        """
        raise NotImplementedError
