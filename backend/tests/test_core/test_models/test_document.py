"""Tests for Document domain model."""
import pytest
from datetime import datetime

from core.models.document import Document, DocumentStatus


class TestDocument:
    """Test Document domain model."""
    
    def test_create_document_with_defaults(self):
        """Test document creation with default values."""
        doc = Document(
            id="test-123",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        
        assert doc.id == "test-123"
        assert doc.filename == "test.pdf"
        assert doc.file_type == "pdf"
        assert doc.page_count == 1
        assert doc.status == DocumentStatus.UPLOADING
        assert doc.created_at is not None
        assert isinstance(doc.created_at, datetime)
        assert doc.metadata == {}
    
    def test_create_document_with_custom_values(self):
        """Test document creation with custom values."""
        custom_time = datetime(2024, 1, 27, 12, 0, 0)
        custom_metadata = {"key": "value"}
        
        doc = Document(
            id="test-456",
            filename="test.png",
            file_type="png",
            file_path="/tmp/test.png",
            page_count=2,
            status=DocumentStatus.COMPLETED,
            created_at=custom_time,
            metadata=custom_metadata,
        )
        
        assert doc.page_count == 2
        assert doc.status == DocumentStatus.COMPLETED
        assert doc.created_at == custom_time
        assert doc.metadata == custom_metadata
    
    def test_is_image(self):
        """Test is_image() method."""
        image_types = ["png", "jpg", "jpeg", "webp", "gif", "tiff"]
        
        for img_type in image_types:
            doc = Document(
                id="test",
                filename=f"test.{img_type}",
                file_type=img_type,
                file_path=f"/tmp/test.{img_type}",
            )
            assert doc.is_image() is True
        
        # Non-image types
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        assert doc.is_image() is False
    
    def test_is_image_case_insensitive(self):
        """Test is_image() is case insensitive."""
        doc = Document(
            id="test",
            filename="test.PNG",
            file_type="PNG",
            file_path="/tmp/test.PNG",
        )
        assert doc.is_image() is True
    
    def test_is_pdf(self):
        """Test is_pdf() method."""
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path="/tmp/test.pdf",
        )
        assert doc.is_pdf() is True
        
        doc = Document(
            id="test",
            filename="test.png",
            file_type="png",
            file_path="/tmp/test.png",
        )
        assert doc.is_pdf() is False
    
    def test_is_pdf_case_insensitive(self):
        """Test is_pdf() is case insensitive."""
        doc = Document(
            id="test",
            filename="test.PDF",
            file_type="PDF",
            file_path="/tmp/test.PDF",
        )
        assert doc.is_pdf() is True
    
    def test_is_supported(self):
        """Test is_supported() method."""
        supported_formats = [
            'pdf', 'doc', 'docx', 'odt',
            'xls', 'xlsx', 'xlst', 'xlsm', 'ods',
            'ppt', 'pptx', 'odp',
            'html', 'epub',
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',
        ]
        
        for fmt in supported_formats:
            doc = Document(
                id="test",
                filename=f"test.{fmt}",
                file_type=fmt,
                file_path=f"/tmp/test.{fmt}",
            )
            assert doc.is_supported() is True
        
        # Unsupported format
        doc = Document(
            id="test",
            filename="test.xyz",
            file_type="xyz",
            file_path="/tmp/test.xyz",
        )
        assert doc.is_supported() is False
    
    def test_is_supported_case_insensitive(self):
        """Test is_supported() is case insensitive."""
        doc = Document(
            id="test",
            filename="test.PDF",
            file_type="PDF",
            file_path="/tmp/test.PDF",
        )
        assert doc.is_supported() is True
    
    def test_validate_requires_id(self):
        """Test validation requires document ID."""
        with pytest.raises(ValueError, match="Document ID is required"):
            Document(
                id="",
                filename="test.pdf",
                file_type="pdf",
                file_path="/tmp/test.pdf",
            )
    
    def test_validate_requires_filename(self):
        """Test validation requires filename."""
        with pytest.raises(ValueError, match="Document filename is required"):
            Document(
                id="test-123",
                filename="",
                file_type="pdf",
                file_path="/tmp/test.pdf",
            )
    
    def test_validate_requires_file_type(self):
        """Test validation requires file type."""
        with pytest.raises(ValueError, match="Document file type is required"):
            Document(
                id="test-123",
                filename="test.pdf",
                file_type="",
                file_path="/tmp/test.pdf",
            )
