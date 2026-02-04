"""File system storage implementation."""
import uuid
from pathlib import Path
from typing import Optional

from core.interfaces.storage_interface import StorageInterface
from core.models.document import Document
from config import settings


class FileStorage(StorageInterface):
    """File system based storage implementation."""
    
    def __init__(self, base_dir: str = None):
        """Initialize file storage.

        Args:
            base_dir: Base directory for file storage
        """
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_content: bytes, filename: str) -> str:
        """Save file and return absolute file path.

        Returns an absolute path so the worker can load the file regardless of
        its current working directory (API and worker may run with different cwd).

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Absolute path where file is saved
        """
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.base_dir / unique_filename

        with open(file_path, 'wb') as f:
            f.write(file_content)

        return str(file_path.resolve())
    
    def load(self, file_path: str) -> bytes:
        """Load file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as bytes
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'rb') as f:
            return f.read()
    
    def delete(self, file_path: str) -> bool:
        """Delete file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully
        """
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def get_page_image(self, document: Document, page_number: int) -> Optional[bytes]:
        """Get page image for document viewer.
        
        Args:
            document: Document entity
            page_number: Page number (0-indexed)
            
        Returns:
            Image bytes or None if not available
        """
        # For image files, return the file itself
        if document.is_image():
            return self.load(document.file_path)
        
        # For PDF, convert to image
        if document.is_pdf():
            try:
                from pdf2image import convert_from_path
                import io
                
                # Convert PDF page to image
                images = convert_from_path(document.file_path)
                if page_number < len(images):
                    img_byte_arr = io.BytesIO()
                    images[page_number].save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue()
                return None
            except ImportError:
                # pdf2image not installed
                return None
            except Exception:
                # PDF conversion failed
                return None
        
        return None
