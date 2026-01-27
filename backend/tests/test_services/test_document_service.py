"""Tests for DocumentService."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import UploadFile

from application.services.document_service import DocumentService
from core.models.document import Document, DocumentStatus
from core.interfaces.storage_interface import StorageInterface


class TestDocumentService:
    """Test DocumentService."""
    
    def test_init_with_storage(self):
        """Test initialization with custom storage."""
        mock_storage = Mock(spec=StorageInterface)
        service = DocumentService(storage=mock_storage)
        assert service.storage == mock_storage
    
    def test_init_without_storage_uses_default(self):
        """Test initialization without storage uses FileStorage."""
        service = DocumentService()
        assert service.storage is not None
    
    @pytest.mark.asyncio
    async def test_create_from_upload(self, temp_dir):
        """Test creating document from upload."""
        service = DocumentService()
        # Override storage base_dir for testing
        service.storage.base_dir = temp_dir
        
        # Create mock UploadFile
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "test.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=b"test content")
        
        document = await service.create_from_upload(upload_file)
        
        assert document.id is not None
        assert document.filename == "test.pdf"
        assert document.file_type == "pdf"
        assert document.page_count == 1
        assert document.status == DocumentStatus.COMPLETED
        assert document.metadata["original_filename"] == "test.pdf"
        assert document.metadata["content_type"] == "application/pdf"
        assert document.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_from_upload_different_file_types(self, temp_dir):
        """Test creating document with different file types."""
        service = DocumentService()
        service.storage.base_dir = temp_dir
        
        file_types = ["pdf", "png", "docx", "xlsx"]
        for file_type in file_types:
            upload_file = Mock(spec=UploadFile)
            upload_file.filename = f"test.{file_type}"
            upload_file.content_type = f"application/{file_type}"
            upload_file.read = AsyncMock(return_value=b"content")
            
            document = await service.create_from_upload(upload_file)
            assert document.file_type == file_type
    
    def test_get_by_id_returns_document(self, temp_dir):
        """Test get_by_id returns document from cache."""
        service = DocumentService()
        service.storage.base_dir = temp_dir
        
        # Create and upload a document
        from unittest.mock import Mock, AsyncMock
        from fastapi import UploadFile
        
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "test.pdf"
        upload_file.content_type = "application/pdf"
        upload_file.read = AsyncMock(return_value=b"test content")
        
        import asyncio
        document = asyncio.run(service.create_from_upload(upload_file))
        
        # Retrieve document
        result = service.get_by_id(document.id)
        assert result is not None
        assert result.id == document.id
        assert result.filename == "test.pdf"
    
    def test_get_by_id_returns_none_when_not_found(self):
        """Test get_by_id returns None when document not found."""
        service = DocumentService()
        result = service.get_by_id("nonexistent-id")
        assert result is None
    
    def test_get_page_image(self, sample_document, temp_dir):
        """Test get_page_image."""
        mock_storage = Mock(spec=StorageInterface)
        mock_storage.get_page_image = Mock(return_value=b"image bytes")
        service = DocumentService(storage=mock_storage)
        
        image_bytes = service.get_page_image(sample_document, 0)
        
        assert image_bytes == b"image bytes"
        mock_storage.get_page_image.assert_called_once_with(sample_document, 0)
    
    def test_get_file_type(self):
        """Test _get_file_type extraction."""
        service = DocumentService()
        
        assert service._get_file_type("document.pdf") == "pdf"
        assert service._get_file_type("image.PNG") == "png"
        assert service._get_file_type("file.docx") == "docx"
        assert service._get_file_type("noextension") == ""
        assert service._get_file_type("file") == ""
