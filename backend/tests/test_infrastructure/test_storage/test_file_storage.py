"""Tests for FileStorage."""
import pytest
from pathlib import Path

from infrastructure.storage.file_storage import FileStorage
from core.models.document import Document, DocumentStatus


class TestFileStorage:
    """Test FileStorage."""
    
    def test_init_creates_directory(self, temp_dir):
        """Test initialization creates base directory."""
        storage = FileStorage(base_dir=str(temp_dir))
        assert temp_dir.exists()
        assert temp_dir.is_dir()
    
    def test_save_file(self, temp_dir):
        """Test saving a file."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"test file content"
        filename = "test.txt"
        
        file_path = storage.save(content, filename)
        
        assert Path(file_path).exists()
        assert Path(file_path).read_bytes() == content
        assert filename in file_path or Path(file_path).suffix == Path(filename).suffix
    
    def test_save_generates_unique_filename(self, temp_dir):
        """Test save generates unique filenames."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"test"
        
        path1 = storage.save(content, "test.txt")
        path2 = storage.save(content, "test.txt")
        
        assert path1 != path2
        assert Path(path1).exists()
        assert Path(path2).exists()
    
    def test_load_file(self, temp_dir):
        """Test loading a file."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"test content"
        file_path = storage.save(content, "test.txt")
        
        loaded_content = storage.load(file_path)
        assert loaded_content == content
    
    def test_load_nonexistent_file_raises_error(self, temp_dir):
        """Test loading nonexistent file raises error."""
        storage = FileStorage(base_dir=str(temp_dir))
        
        with pytest.raises(FileNotFoundError):
            storage.load("/nonexistent/path/file.txt")
    
    def test_delete_file(self, temp_dir):
        """Test deleting a file."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"test"
        file_path = storage.save(content, "test.txt")
        
        assert Path(file_path).exists()
        result = storage.delete(file_path)
        
        assert result is True
        assert not Path(file_path).exists()
    
    def test_delete_nonexistent_file_returns_false(self, temp_dir):
        """Test deleting nonexistent file returns False."""
        storage = FileStorage(base_dir=str(temp_dir))
        
        result = storage.delete("/nonexistent/path/file.txt")
        assert result is False
    
    def test_get_page_image_for_image(self, temp_dir):
        """Test get_page_image for image file."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"fake image content"
        file_path = storage.save(content, "test.png")
        
        doc = Document(
            id="test",
            filename="test.png",
            file_type="png",
            file_path=file_path,
        )
        
        image_bytes = storage.get_page_image(doc, 0)
        assert image_bytes == content
    
    def test_get_page_image_for_pdf_returns_none(self, temp_dir):
        """Test get_page_image for PDF returns None (not implemented)."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"fake pdf content"
        file_path = storage.save(content, "test.pdf")
        
        doc = Document(
            id="test",
            filename="test.pdf",
            file_type="pdf",
            file_path=file_path,
        )
        
        # PDF to image conversion not implemented yet
        image_bytes = storage.get_page_image(doc, 0)
        assert image_bytes is None
    
    def test_get_page_image_unsupported_type_returns_none(self, temp_dir):
        """Test get_page_image for unsupported type returns None."""
        storage = FileStorage(base_dir=str(temp_dir))
        content = b"test"
        file_path = storage.save(content, "test.doc")
        
        doc = Document(
            id="test",
            filename="test.doc",
            file_type="doc",
            file_path=file_path,
        )
        
        image_bytes = storage.get_page_image(doc, 0)
        assert image_bytes is None
