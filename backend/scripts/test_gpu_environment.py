#!/usr/bin/env python3
"""GPU environment verification script.

This script checks:
1. PyTorch installation and CUDA availability
2. GPU device information
3. Basic GPU tensor operations
4. Required dependencies for parsers
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_pytorch():
    """Check PyTorch installation and CUDA availability."""
    print_section("PyTorch & CUDA Check")
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.is_available()}")
            print(f"✓ CUDA version: {torch.version.cuda}")
            print(f"✓ cuDNN version: {torch.backends.cudnn.version()}")
            print(f"✓ GPU count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"\n  GPU {i}: {props.name}")
                print(f"    - Total memory: {props.total_memory / 1e9:.2f} GB")
                print(f"    - Compute capability: {props.major}.{props.minor}")
                print(f"    - Multi-processor count: {props.multi_processor_count}")
            
            # Test basic GPU operation
            print("\n  Testing GPU tensor operation...")
            x = torch.randn(3, 3).cuda()
            y = torch.randn(3, 3).cuda()
            z = torch.matmul(x, y)
            print(f"  ✓ Successfully created and operated tensors on GPU")
            print(f"  ✓ Tensor device: {x.device}")
            
            return True
        else:
            print("✗ CUDA is not available")
            print("  This means GPU acceleration is not available.")
            return False
            
    except ImportError:
        print("✗ PyTorch is not installed")
        print("  Install with: pip install torch")
        return False
    except Exception as e:
        print(f"✗ Error checking PyTorch: {e}")
        return False


def check_dependencies():
    """Check required dependencies for parsers."""
    print_section("Parser Dependencies Check")
    
    dependencies = {
        "docling": "docling",
        "chandra-ocr": "chandra",
        "transformers": "transformers",
        "pdf2image": "pdf2image",
        "PIL": "PIL",
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} not installed")
            all_ok = False
    
    return all_ok


def check_chandra_import():
    """Check if Chandra parser can be imported."""
    print_section("Chandra Parser Import Check")
    
    try:
        from infrastructure.parsers.chandra_parser import ChandraParser
        print("✓ ChandraParser can be imported")
        return True
    except ImportError as e:
        print(f"✗ Cannot import ChandraParser: {e}")
        return False
    except RuntimeError as e:
        if "GPU" in str(e) or "CUDA" in str(e):
            print(f"⚠ ChandraParser requires GPU: {e}")
            return False
        print(f"✗ Error importing ChandraParser: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def check_docling_import():
    """Check if Docling parser can be imported."""
    print_section("Docling Parser Import Check")
    
    try:
        from infrastructure.parsers.docling_parser import DoclingParser
        print("✓ DoclingParser can be imported")
        return True
    except ImportError as e:
        print(f"✗ Cannot import DoclingParser: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("  GPU Environment Verification")
    print("="*60)
    
    results = {
        "pytorch": check_pytorch(),
        "dependencies": check_dependencies(),
        "chandra_import": check_chandra_import(),
        "docling_import": check_docling_import(),
    }
    
    print_section("Summary")
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    if all_passed:
        print("\n✓ All checks passed! GPU environment is ready.")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

