"""Docling parser implementation."""
from typing import List

from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult, Block


class DoclingParser(BaseParser):
    """Parser using Docling library."""
    
    def __init__(self, config=None):
        """Initialize Docling parser.
        
        Args:
            config: Parser configuration
        """
        super().__init__(config)
        self._converter = None
    
    def get_name(self) -> str:
        """Get parser name."""
        return "docling"
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [
            'pdf', 'doc', 'docx', 'odt',  # Documents
            'xls', 'xlsx', 'ods',  # Spreadsheets
            'ppt', 'pptx', 'odp',  # Presentations
            'html', 'epub',  # Web & Books
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',  # Images
            'wav', 'mp3', 'vtt',  # Audio/Video
        ]
    
    def _get_converter(self):
        """Get or create Docling converter (lazy loading)."""
        if self._converter is None:
            try:
                from docling.document_converter import DocumentConverter
                self._converter = DocumentConverter()
            except ImportError:
                raise ImportError(
                    "Docling is not installed. Install it with: pip install docling"
                )
        return self._converter
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using Docling library.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
        """
        converter = self._get_converter()
        
        # Convert document
        result = converter.convert(document.file_path)
        
        # Convert DoclingDocument to ParseResult
        blocks = []
        
        # Export to markdown for text extraction
        markdown_content = result.document.export_to_markdown()
        
        # Create blocks from markdown (simplified)
        # TODO: More sophisticated conversion from DoclingDocument structure
        blocks.append(
            Block(
                type="text",
                text=markdown_content,
                metadata={
                    "parser": "docling",
                    "file_type": document.file_type,
                },
            )
        )
        
        return ParseResult(
            document_id=document.id,
            blocks=blocks,
            metadata={
                "parser": self.get_name(),
                "file_type": document.file_type,
                "format": "markdown",
            },
        )
