"""Parser interface (port) for document parsing."""
from abc import ABC, abstractmethod
from typing import List

from core.models.document import Document
from core.models.parse_result import ParseResult


class ParserInterface(ABC):
    """Abstract interface for document parsers."""
    
    @abstractmethod
    def parse(self, document: Document) -> ParseResult:
        """Parse a document and return structured result.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats.
        
        Returns:
            List of supported file extensions (e.g., ['pdf', 'png', 'jpg'])
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get parser name.
        
        Returns:
            Parser identifier name
        """
        pass
