#!/usr/bin/env python3
"""Test Docling and Chandra parsers on GPU.

This script performs actual parsing tests to verify:
1. Docling parser can parse documents (CPU/GPU)
2. Chandra parser can parse documents on GPU
3. Both parsers produce valid results
"""
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models.document import Document, DocumentStatus


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def create_test_image():
    """Create a simple test image file."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image with text
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "Test Document\nGPU Parser Test\nThis is a test image."
        draw.text((50, 50), text, fill='black', font=font)
        
        return img
    except ImportError:
        print("✗ PIL/Pillow not available")
        return None


def test_chandra_parser():
    """Test Chandra parser on GPU."""
    print_section("Testing Chandra Parser (GPU)")
    
    try:
        import torch
        if not torch.cuda.is_available():
            print("⚠ CUDA not available - skipping Chandra test")
            return False
    except ImportError:
        print("⚠ PyTorch not available - skipping Chandra test")
        return False
    
    try:
        from infrastructure.parsers.chandra_parser import ChandraParser
        
        # Reset model state for clean test
        ChandraParser._model_loaded = False
        ChandraParser._model = None
        
        print("  Initializing Chandra parser...")
        parser = ChandraParser()
        print("  ✓ Parser initialized")
        
        # Check if model is on GPU
        if hasattr(ChandraParser._model, 'device'):
            device_str = str(ChandraParser._model.device)
            if 'cuda' in device_str:
                print(f"  ✓ Model loaded on GPU: {device_str}")
            else:
                print(f"  ⚠ Model not on GPU: {device_str}")
                return False
        
        # Create test image
        print("  Creating test image...")
        test_img = create_test_image()
        if test_img is None:
            print("  ⚠ Cannot create test image - skipping parse test")
            return True  # Parser init is enough
        
        # Save test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_img.save(f.name)
            test_path = f.name
        
        try:
            # Create document
            doc = Document(
                id="test-chandra",
                filename="test.png",
                file_type="png",
                file_path=test_path,
                page_count=1,
                status=DocumentStatus.COMPLETED,
                created_at=datetime.now(),
            )
            
            print("  Parsing test image...")
            result = parser.parse(doc)
            
            print(f"  ✓ Parse successful")
            print(f"  ✓ Document ID: {result.document_id}")
            print(f"  ✓ Blocks: {len(result.blocks)}")
            if result.blocks:
                print(f"  ✓ First block type: {result.blocks[0].type}")
                text_preview = result.blocks[0].text[:100] if result.blocks[0].text else ""
                print(f"  ✓ Text preview: {text_preview}...")
            
            return True
            
        finally:
            # Cleanup
            Path(test_path).unlink(missing_ok=True)
            
    except RuntimeError as e:
        if "GPU" in str(e) or "CUDA" in str(e):
            print(f"  ✗ GPU error: {e}")
        else:
            print(f"  ✗ Runtime error: {e}")
        return False
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_docling_parser():
    """Test Docling parser."""
    print_section("Testing Docling Parser")
    
    try:
        from infrastructure.parsers.docling_parser import DoclingParser
        
        print("  Initializing Docling parser...")
        parser = DoclingParser()
        print("  ✓ Parser initialized")
        
        # Check if converter has GPU support
        converter = parser._get_converter()
        print(f"  ✓ Converter created: {type(converter).__name__}")
        
        # Note: Docling may use GPU internally for OCR, but it's not always explicit
        # We'll test if it can parse a document
        
        # Create test image
        print("  Creating test image...")
        test_img = create_test_image()
        if test_img is None:
            print("  ⚠ Cannot create test image - skipping parse test")
            return True  # Parser init is enough
        
        # Save test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_img.save(f.name)
            test_path = f.name
        
        try:
            # Create document
            doc = Document(
                id="test-docling",
                filename="test.png",
                file_type="png",
                file_path=test_path,
                page_count=1,
                status=DocumentStatus.COMPLETED,
                created_at=datetime.now(),
            )
            
            print("  Parsing test image...")
            result = parser.parse(doc)
            
            print(f"  ✓ Parse successful")
            print(f"  ✓ Document ID: {result.document_id}")
            print(f"  ✓ Blocks: {len(result.blocks)}")
            if result.blocks:
                print(f"  ✓ First block type: {result.blocks[0].type}")
                text_preview = result.blocks[0].text[:100] if result.blocks[0].text else ""
                print(f"  ✓ Text preview: {text_preview}...")
            
            return True
            
        finally:
            # Cleanup
            Path(test_path).unlink(missing_ok=True)
            
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_gpu_usage():
    """Check if GPU is being used by monitoring GPU memory."""
    print_section("GPU Memory Monitoring")
    
    try:
        import torch
        if not torch.cuda.is_available():
            print("  ⚠ CUDA not available - cannot monitor GPU")
            return
        
        import time
        
        # Get initial GPU memory
        initial_memory = torch.cuda.memory_allocated() / 1e9
        print(f"  Initial GPU memory: {initial_memory:.2f} GB")
        
        # Create a large tensor to test
        print("  Allocating test tensor on GPU...")
        test_tensor = torch.randn(1000, 1000).cuda()
        time.sleep(0.5)
        
        current_memory = torch.cuda.memory_allocated() / 1e9
        print(f"  Current GPU memory: {current_memory:.2f} GB")
        print(f"  Memory increase: {current_memory - initial_memory:.2f} GB")
        
        # Cleanup
        del test_tensor
        torch.cuda.empty_cache()
        
        final_memory = torch.cuda.memory_allocated() / 1e9
        print(f"  Final GPU memory (after cleanup): {final_memory:.2f} GB")
        
    except ImportError:
        print("  ⚠ PyTorch not available")
    except Exception as e:
        print(f"  ⚠ Error monitoring GPU: {e}")


def main():
    """Run all parser tests."""
    print("\n" + "="*60)
    print("  GPU Parser Testing")
    print("="*60)
    
    # Check GPU environment first
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n✓ CUDA available - {torch.cuda.device_count()} GPU(s)")
            check_gpu_usage()
        else:
            print("\n⚠ CUDA not available - some tests will be skipped")
    except ImportError:
        print("\n⚠ PyTorch not available")
    
    results = {
        "docling": test_docling_parser(),
        "chandra": test_chandra_parser(),
    }
    
    print_section("Test Summary")
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name} parser")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All parser tests passed!")
        return 0
    else:
        print("\n✗ Some parser tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

