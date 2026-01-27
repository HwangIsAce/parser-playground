"""Storage interface (port) for file storage."""
from abc import ABC, abstractmethod
from typing import Optional

from core.models.document import Document


class StorageInterface(ABC):
    """Abstract interface for file storage."""
    
    @abstractmethod
    def save(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path where file is saved
        """
        pass
    
    @abstractmethod
    def load(self, file_path: str) -> bytes:
        """Load file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as bytes
        """
        pass
    
    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """Delete file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    def get_page_image(self, document: Document, page_number: int) -> Optional[bytes]:
        """Get page image for document viewer.
        
        Args:
            document: Document entity
            page_number: Page number (0-indexed)
            
        Returns:
            Image bytes or None if not available
        """
        pass
