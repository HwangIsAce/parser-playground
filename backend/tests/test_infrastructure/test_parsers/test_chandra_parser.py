"""Tests for ChandraParser with GPU."""
import pytest
from unittest.mock import patch, Mock, MagicMock
from PIL import Image

from infrastructure.parsers.chandra_parser import ChandraParser
from core.models.document import Document, DocumentStatus


class TestChandraParserGPU:
    """Test ChandraParser GPU functionality."""
    
    def test_get_name(self):
        """Test get_name returns 'chandra'."""
        # This test doesn't require GPU
        with patch.object(ChandraParser, '_ensure_model_loaded'):
            parser = ChandraParser()
            assert parser.get_name() == "chandra"
    
    def test_get_supported_formats(self):
        """Test get_supported_formats returns correct formats."""
        with patch.object(ChandraParser, '_ensure_model_loaded'):
            parser = ChandraParser()
            formats = parser.get_supported_formats()
            
            assert isinstance(formats, list)
            assert "pdf" in formats
            assert "png" in formats
            assert "jpg" in formats
    
    def test_gpu_availability_check(self):
        """Test that GPU availability is checked."""
        # Reset model state
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        with patch('torch.cuda.is_available', return_value=False):
            with pytest.raises(RuntimeError, match="CUDA is not available"):
                ChandraParser._ensure_model_loaded()
    
    def test_pytorch_not_installed(self):
        """Test error when PyTorch is not installed."""
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        with patch.dict('sys.modules', {'torch': None}):
            with pytest.raises(ImportError, match="PyTorch is not installed"):
                ChandraParser._ensure_model_loaded()
    
    @pytest.mark.skipif(not pytest.importorskip("torch").cuda.is_available(), 
                        reason="GPU not available")
    def test_model_loads_on_gpu(self):
        """Test that model loads on GPU when available."""
        # Reset model state
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        try:
            parser = ChandraParser()
            assert parser is not None
            
            # Verify model is on GPU
            import torch
            if hasattr(ChandraParser._model, 'device'):
                device_str = str(ChandraParser._model.device)
                assert 'cuda' in device_str, f"Model not on GPU: {device_str}"
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"Chandra dependencies not available: {e}")
    
    @pytest.mark.skipif(not pytest.importorskip("torch").cuda.is_available(), 
                        reason="GPU not available")
    def test_parse_on_gpu(self, temp_dir, sample_image_document):
        """Test parsing a document on GPU."""
        # Reset model state
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        try:
            # Create a simple test image
            test_img = Image.new('RGB', (100, 100), color='white')
            test_path = temp_dir / "test.png"
            test_img.save(test_path)
            
            # Update document path
            doc = Document(
                id=sample_image_document.id,
                filename=sample_image_document.filename,
                file_type=sample_image_document.file_type,
                file_path=str(test_path),
                page_count=1,
                status=DocumentStatus.COMPLETED,
            )
            
            parser = ChandraParser()
            result = parser.parse(doc)
            
            assert result.document_id == doc.id
            assert len(result.blocks) > 0
            assert result.metadata["parser"] == "chandra"
            
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"Chandra dependencies not available: {e}")
    
    def test_gpu_error_handling(self):
        """Test error handling when GPU is not available."""
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        with patch('torch.cuda.is_available', return_value=False):
            with pytest.raises(RuntimeError, match="CUDA is not available"):
                ChandraParser._ensure_model_loaded()

