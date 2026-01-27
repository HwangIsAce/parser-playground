"""Unstructured library parser implementation."""
from typing import List

from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult


class UnstructuredParser(BaseParser):
    """Parser using unstructured library."""
    
    def get_name(self) -> str:
        """Get parser name."""
        raise NotImplementedError
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        raise NotImplementedError
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using unstructured library.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
        """
        raise NotImplementedError
