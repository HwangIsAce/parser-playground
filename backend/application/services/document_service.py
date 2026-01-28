"""Document service for document management."""
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Tuple

from fastapi import UploadFile

from core.models.document import Document, DocumentStatus
from core.models.parse_result import ParseResult
from core.interfaces.storage_interface import StorageInterface
from infrastructure.storage.file_storage import FileStorage
from infrastructure.queue.redis_queue import redis_conn


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
            - Uses Redis for document storage (shared across processes)
            - Uses Redis for parse results (key: (document_id, page_number, mode))
        """
        self.storage = storage or FileStorage()
        self._redis = redis_conn
        self._doc_key_prefix = "document:"
        self._parse_result_key_prefix = "parse_result:"
    
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
        
        # Store in Redis
        key = self._document_key(document.id)
        self._redis.set(key, self._serialize_document(document))
        
        return document
    
    def _document_key(self, document_id: str) -> str:
        """Get Redis key for document."""
        return f"{self._doc_key_prefix}{document_id}"
    
    def _parse_result_key(self, document_id: str, page_number: int, mode: str) -> str:
        """Get Redis key for parse result."""
        return f"{self._parse_result_key_prefix}{document_id}:{page_number}:{mode}"
    
    def _serialize_document(self, document: Document) -> str:
        """Serialize document to JSON string."""
        data = {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_path": document.file_path,
            "page_count": document.page_count,
            "status": document.status.value,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "metadata": document.metadata or {},
        }
        return json.dumps(data)
    
    def _deserialize_document(self, data: str) -> Document:
        """Deserialize document from JSON string."""
        doc_data = json.loads(data)
        
        document = Document(
            id=doc_data["id"],
            filename=doc_data["filename"],
            file_type=doc_data["file_type"],
            file_path=doc_data["file_path"],
            page_count=doc_data.get("page_count", 1),
            status=DocumentStatus(doc_data["status"]),
            created_at=datetime.fromisoformat(doc_data["created_at"]) if doc_data.get("created_at") else None,
            metadata=doc_data.get("metadata", {}),
        )
        return document
    
    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document entity or None if not found
            
        Note:
            - Uses Redis for document retrieval (shared across processes)
        """
        key = self._document_key(document_id)
        data = self._redis.get(key)
        if not data:
            return None
        
        # Decode bytes to string if needed
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return self._deserialize_document(data)
    
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
    
    def _serialize_parse_result(self, parse_result: ParseResult) -> str:
        """Serialize parse result to JSON string."""
        return json.dumps(parse_result.to_dict())
    
    def _deserialize_parse_result(self, data: str) -> ParseResult:
        """Deserialize parse result from JSON string."""
        from core.models.parse_result import Block, ParseResult
        
        result_data = json.loads(data)
        
        blocks = [
            Block(
                type=block_data["type"],
                text=block_data["text"],
                coordinates=block_data.get("coordinates"),
                metadata=block_data.get("metadata", {}),
                page=block_data.get("page"),
                element_id=block_data.get("element_id"),
                content=block_data.get("content"),
            )
            for block_data in result_data.get("blocks", [])
        ]
        
        return ParseResult(
            document_id=result_data["document_id"],
            blocks=blocks,
            metadata=result_data.get("metadata", {}),
            full_content=result_data.get("content"),
            usage=result_data.get("usage"),
        )
    
    def save_parse_result(
        self,
        document_id: str,
        page_number: int,
        mode: str,
        parse_result: ParseResult
    ) -> None:
        """Save parse result to Redis.
        
        Args:
            document_id: Document ID
            page_number: Page number (0-indexed)
            mode: Parse mode ('basic' or 'enhance')
            parse_result: ParseResult to cache
            
        Note:
            - Uses Redis for parse result storage (shared across processes)
        """
        key = self._parse_result_key(document_id, page_number, mode)
        self._redis.set(key, self._serialize_parse_result(parse_result))
    
    def get_parse_result(
        self,
        document_id: str,
        page_number: int,
        mode: str
    ) -> Optional[ParseResult]:
        """Get parse result from Redis.
        
        Args:
            document_id: Document ID
            page_number: Page number (0-indexed)
            mode: Parse mode ('basic' or 'enhance')
            
        Returns:
            ParseResult or None if not found
        """
        key = self._parse_result_key(document_id, page_number, mode)
        data = self._redis.get(key)
        if not data:
            return None
        
        # Decode bytes to string if needed
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return self._deserialize_parse_result(data)
    
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
