"""Document service for document management."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Tuple

from fastapi import UploadFile

from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult
from core.interfaces.storage_interface import StorageInterface
from infrastructure.storage.file_storage import FileStorage


class DocumentService:
    """Service for document management operations.
    
    Note: Currently designed for page-level processing.
    Each Document represents a single page.
    """
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        """Initialize document service.
        
        Args:
            storage: Storage implementation (defaults to FileStorage)
            
        Note:
            - Uses dependency injection for testability
            - Defaults to FileStorage if not provided
            - Uses in-memory cache for document storage (can be extended to DB)
            - Uses in-memory cache for parse results (key: (document_id, page_number, mode))
        """
        self.storage = storage or FileStorage()
        self._documents: Dict[str, Document] = {}  # In-memory cache
        self._parse_results: Dict[Tuple[str, int, str], ParseResult] = {}  # Parse result cache
    
    async def create_from_upload(self, upload_file: UploadFile) -> Document:
        """Create a single-page document from uploaded file.
        
        Args:
            upload_file: FastAPI UploadFile object
            
        Returns:
            Document entity (single page)
            
        Note:
            - Currently processes single page only (page_count=1)
            - For PDFs, the entire file is saved but treated as single page
            - Future: Can be extended to extract specific pages from PDFs
        """
        # Read file content
        file_content = await upload_file.read()
        
        # Save file to storage (UUID-based unique filename)
        file_path = self.storage.save(file_content, upload_file.filename)
        
        # Extract file type
        file_type = self._get_file_type(upload_file.filename)
        
        # Create page-level Document entity
        document = Document(
            id=str(uuid.uuid4()),
            filename=upload_file.filename,
            file_type=file_type,
            file_path=file_path,
            page_count=1,  # Page-level: always 1
            status=DocumentStatus.COMPLETED,
            created_at=datetime.now(),
            metadata={
                "original_filename": upload_file.filename,
                "content_type": upload_file.content_type,
            },
        )
        
        # Store in cache
        self._documents[document.id] = document
        
        return document
    
    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document entity or None if not found
            
        Note:
            - Uses in-memory cache for document retrieval
            - Future: Can be extended to query from database
        """
        return self._documents.get(document_id)
    
    def get_page_image(self, document: Document, page_number: int) -> Optional[bytes]:
        """Get page image for document viewer.
        
        Args:
            document: Document entity (single page)
            page_number: Page number (0-indexed)
            
        Returns:
            Image bytes or None if not available
            
        Note:
            - For page-level processing, page_number should always be 0
            - Future: Can be extended to support multi-page documents
        """
        # Page-level processing: page_number should be 0
        if page_number != 0:
            # For now, we only support single page (page 0)
            # Future: Can validate page_number against document.page_count
            pass
        
        return self.storage.get_page_image(document, page_number)
    
    def save_parse_result(
        self,
        document_id: str,
        page_number: int,
        mode: str,
        parse_result: ParseResult
    ) -> None:
        """Save parse result to cache.
        
        Args:
            document_id: Document ID
            page_number: Page number (0-indexed)
            mode: Parse mode ('basic' or 'enhance')
            parse_result: ParseResult to cache
            
        Note:
            - Uses in-memory cache (key: (document_id, page_number, mode))
            - Future: Can be extended to persist to database
        """
        key = (document_id, page_number, mode)
        self._parse_results[key] = parse_result
    
    def get_parse_result(
        self,
        document_id: str,
        page_number: int,
        mode: str
    ) -> Optional[ParseResult]:
        """Get parse result from cache.
        
        Args:
            document_id: Document ID
            page_number: Page number (0-indexed)
            mode: Parse mode ('basic' or 'enhance')
            
        Returns:
            ParseResult or None if not found
        """
        key = (document_id, page_number, mode)
        return self._parse_results.get(key)
    
    def _get_file_type(self, filename: str) -> str:
        """Extract file type from filename.
        
        Args:
            filename: Filename with extension (e.g., "document.pdf")
            
        Returns:
            File extension without dot (e.g., "pdf")
            
        Examples:
            "document.pdf" -> "pdf"
            "image.png" -> "png"
            "file" -> "" (no extension)
        """
        from pathlib import Path
        
        ext = Path(filename).suffix  # ".pdf"
        # Remove dot and convert to lowercase
        return ext.lstrip('.').lower() if ext else ''
