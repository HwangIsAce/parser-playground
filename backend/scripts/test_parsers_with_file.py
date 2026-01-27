#!/usr/bin/env python3
"""Test Docling and Chandra parsers on GPU with actual document.

This script tests parsers with a real document image and saves results.
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models.document import Document, DocumentStatus
from application.services.parser_service import ParserService


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def save_result(parser_name: str, mode: str, result, output_dir: Path):
    """Save parsing result to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save markdown result
    markdown_file = output_dir / f"{parser_name}_{mode}_result.md"
    if result.blocks and result.blocks[0].text:
        markdown_file.write_text(result.blocks[0].text, encoding='utf-8')
        print(f"  ✓ Saved markdown: {markdown_file}")
    
    # Save JSON result (using to_dict() to include all new schema fields)
    json_file = output_dir / f"{parser_name}_{mode}_result.json"
    result_dict = result.to_dict()  # Use to_dict() to get all fields including new schema
    result_dict["timestamp"] = datetime.now().isoformat()
    
    # Add summary info
    result_dict["summary"] = {
        "blocks_count": len(result.blocks),
        "has_coordinates": any(b.coordinates is not None for b in result.blocks),
        "has_content": any(b.content is not None for b in result.blocks),
        "has_full_content": result.full_content is not None,
        "has_usage": result.usage is not None,
    }
    
    json_file.write_text(json.dumps(result_dict, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✓ Saved JSON: {json_file}")
    
    # Print schema validation
    print(f"\n  Schema Validation:")
    print(f"    - Blocks with coordinates: {sum(1 for b in result.blocks if b.coordinates)}")
    print(f"    - Blocks with content: {sum(1 for b in result.blocks if b.content)}")
    print(f"    - Full content available: {result.full_content is not None}")
    print(f"    - Usage info available: {result.usage is not None}")


def test_parser_with_file(input_file: Path, parser_name: str, mode: str, output_dir: Path):
    """Test a parser with actual file."""
    print_section(f"Testing {parser_name.upper()} Parser ({mode} mode)")
    
    if not input_file.exists():
        print(f"  ✗ Input file not found: {input_file}")
        return False
    
    try:
        # Check GPU for Chandra
        if parser_name == "chandra" or mode == "enhance":
            import torch
            if not torch.cuda.is_available():
                print("  ✗ CUDA not available - Chandra requires GPU")
                return False
            print(f"  ✓ GPU available: {torch.cuda.get_device_name(0)}")
        
        # Create document
        doc = Document(
            id=f"test-{parser_name}-{mode}",
            filename=input_file.name,
            file_type=input_file.suffix[1:],  # Remove dot
            file_path=str(input_file),
            page_count=1,
            status=DocumentStatus.COMPLETED,
            created_at=datetime.now(),
        )
        
        # Parse document
        print(f"  Parsing: {input_file.name}")
        service = ParserService()
        result = service.parse_document(doc, mode=mode)
        
        print(f"  ✓ Parse successful")
        print(f"  ✓ Document ID: {result.document_id}")
        print(f"  ✓ Blocks: {len(result.blocks)}")
        
        if result.blocks:
            text_preview = result.blocks[0].text[:100] if result.blocks[0].text else ""
            print(f"  ✓ Text preview: {text_preview}...")
        
        # Save results
        save_result(parser_name, mode, result, output_dir)
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run parser tests with actual document."""
    print("\n" + "="*60)
    print("  GPU Parser Testing with Real Document")
    print("="*60)
    
    # Setup paths
    backend_dir = Path(__file__).parent.parent
    input_dir = backend_dir / "tests" / "data" / "input"
    output_dir = backend_dir / "tests" / "data" / "output"
    
    # Find PNG file in input directory (handles unicode filenames)
    png_files = list(input_dir.glob("*.png"))
    if not png_files:
        print(f"\n✗ No PNG files found in: {input_dir}")
        print("  Please ensure the file exists at the expected location.")
        return 1
    
    input_file = png_files[0]  # Use first PNG file found
    print(f"\nFound input file: {input_file.name}")
    
    print(f"\nInput file: {input_file}")
    print(f"Output directory: {output_dir}")
    
    results = {}
    
    # Test Docling (basic mode)
    results["docling"] = test_parser_with_file(
        input_file, "docling", "basic", output_dir
    )
    
    # Test Chandra (enhance mode)
    results["chandra"] = test_parser_with_file(
        input_file, "chandra", "enhance", output_dir
    )
    
    # Summary
    print_section("Test Summary")
    
    for parser_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {parser_name} parser")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n✓ All tests passed! Results saved to: {output_dir}")
        return 0
    else:
        print(f"\n✗ Some tests failed. Check output directory: {output_dir}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

