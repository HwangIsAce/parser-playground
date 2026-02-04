#!/usr/bin/env python3
"""Test Docling and Chandra parsers (config-aware).

Uses ParserService so that:
- If PARSER_API_ENABLED=True: tests remote parsers at PARSER_API_BASE_URL (e.g. 194.68.245.19:22159).
- If False: tests local Docling/Chandra parsers (Chandra requires local CUDA).
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

        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40
            )
        except OSError:
            font = ImageFont.load_default()
        text = "Test Document\nParser Test\nThis is a test image."
        draw.text((50, 50), text, fill='black', font=font)
        return img
    except ImportError:
        print("  ✗ PIL/Pillow not available")
        return None


def test_parser_via_service(mode: str, parser_label: str) -> bool:
    """Test a parser via ParserService (respects PARSER_API_ENABLED and config)."""
    print_section(f"Testing {parser_label} (mode={mode})")

    try:
        from config import settings
        from application.services.parser_service import ParserService

        if settings.PARSER_API_ENABLED:
            url = getattr(settings, 'PARSER_API_BASE_URL', '')
            print(f"  Using REMOTE parser at: {url}")
        else:
            print("  Using LOCAL parser")

        # Chandra (enhance) with local parser requires CUDA
        if not settings.PARSER_API_ENABLED and mode == "enhance":
            try:
                import torch
                if not torch.cuda.is_available():
                    print("  ⚠ CUDA not available - skipping local Chandra test")
                    return False
            except ImportError:
                print("  ⚠ PyTorch not available - skipping local Chandra test")
                return False

        service = ParserService()
        print("  Creating test image...")
        test_img = create_test_image()
        if test_img is None:
            return False

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_img.save(f.name)
            test_path = f.name

        try:
            doc = Document(
                id=f"test-{mode}",
                filename="test.png",
                file_type="png",
                file_path=test_path,
                page_count=1,
                status=DocumentStatus.COMPLETED,
                created_at=datetime.now(),
            )
            print(f"  Parsing (mode={mode})...")
            result = service.parse_document(doc, mode=mode)
            print(f"  ✓ Parse successful")
            print(f"  ✓ Document ID: {result.document_id}")
            print(f"  ✓ Blocks: {len(result.blocks)}")
            if result.blocks:
                text_preview = (
                    (result.blocks[0].text or "")[:80].replace("\n", " ")
                )
                print(f"  ✓ Text preview: {text_preview}...")
            return True
        finally:
            Path(test_path).unlink(missing_ok=True)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run parser tests via ParserService (config-aware)."""
    print("\n" + "=" * 60)
    print("  Parser test (ParserService — respects config)")
    print("=" * 60)

    try:
        from config import settings
        if settings.PARSER_API_ENABLED:
            print(f"\n  PARSER_API_ENABLED=True → {settings.PARSER_API_BASE_URL}")
        else:
            print("\n  PARSER_API_ENABLED=False → local Docling/Chandra")
    except Exception as e:
        print(f"\n  ✗ Failed to load config: {e}")
        return 1

    results = {
        "docling (basic)": test_parser_via_service("basic", "Docling"),
        "chandra (enhance)": test_parser_via_service("enhance", "Chandra"),
    }

    print_section("Test Summary")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All parser tests passed!")
        return 0
    print("\n✗ Some parser tests failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
