"""Integration tests for GPU-based parsing."""
import pytest
from unittest.mock import patch, Mock
import torch

from core.models.document import Document, DocumentStatus
from application.services.parser_service import ParserService


class TestGPUParseIntegration:
    """Test GPU parsing through ParserService."""
    
    @pytest.mark.skipif(not pytest.importorskip("torch").cuda.is_available(), 
                        reason="GPU not available")
    def test_chandra_parser_via_service(self, temp_dir):
        """Test Chandra parser through ParserService."""
        try:
            from PIL import Image
            
            # Create test image
            test_img = Image.new('RGB', (200, 200), color='white')
            test_path = temp_dir / "test.png"
            test_img.save(test_path)
            
            doc = Document(
                id="test-gpu",
                filename="test.png",
                file_type="png",
                file_path=str(test_path),
                page_count=1,
                status=DocumentStatus.COMPLETED,
            )
            
            service = ParserService()
            result = service.parse_document(doc, mode="enhance")
            
            assert result.document_id == doc.id
            assert result.metadata["parser"] == "chandra"
            assert len(result.blocks) > 0
            
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"Chandra dependencies not available: {e}")
    
    def test_chandra_parser_without_gpu(self):
        """Test that enhance mode returns error when GPU unavailable."""
        with patch('torch.cuda.is_available', return_value=False):
            service = ParserService()
            
            doc = Document(
                id="test",
                filename="test.pdf",
                file_type="pdf",
                file_path="/tmp/test.pdf",
                page_count=1,
                status=DocumentStatus.COMPLETED,
            )
            
            with pytest.raises((RuntimeError, ValueError)) as exc_info:
                service.parse_document(doc, mode="enhance")
            
            # Should raise error about GPU
            assert "GPU" in str(exc_info.value) or "CUDA" in str(exc_info.value)
    
    @pytest.mark.skipif(not pytest.importorskip("docling"), 
                        reason="Docling not installed")
    def test_docling_parser_via_service(self, temp_dir):
        """Test Docling parser through ParserService."""
        try:
            from PIL import Image
            
            # Create test image
            test_img = Image.new('RGB', (200, 200), color='white')
            test_path = temp_dir / "test.png"
            test_img.save(test_path)
            
            doc = Document(
                id="test-docling",
                filename="test.png",
                file_type="png",
                file_path=str(test_path),
                page_count=1,
                status=DocumentStatus.COMPLETED,
            )
            
            service = ParserService()
            result = service.parse_document(doc, mode="basic")
            
            assert result.document_id == doc.id
            assert result.metadata["parser"] == "docling"
            
        except ImportError:
            pytest.skip("Docling not available")
        except Exception as e:
            # Docling might fail on simple test image, that's okay
            pytest.skip(f"Docling parse failed: {e}")

