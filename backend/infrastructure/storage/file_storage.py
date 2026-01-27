"""File system storage implementation."""
from typing import Optional

from core.interfaces.storage_interface import StorageInterface
from core.models.document import Document


class FileStorage(StorageInterface):
    """File system based storage implementation."""
    
    def __init__(self, base_dir: str = None):
        """Initialize file storage.
        
        Args:
            base_dir: Base directory for file storage
        """
        pass
    
    def save(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path where file is saved
        """
        raise NotImplementedError
    
    def load(self, file_path: str) -> bytes:
        """Load file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as bytes
        """
        raise NotImplementedError
    
    def delete(self, file_path: str) -> bool:
        """Delete file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully
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
