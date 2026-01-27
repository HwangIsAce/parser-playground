"""Parser service for document parsing orchestration."""
from typing import Optional

from core.models.document import Document
from core.models.parse_result import ParseResult
from core.interfaces.parser_interface import ParserInterface


class ParserService:
    """Service for document parsing operations."""
    
    def __init__(self):
        """Initialize parser service."""
        pass
    
    def parse_document(
        self,
        document: Document,
        parser_name: Optional[str] = None
    ) -> ParseResult:
        """Parse a document using specified or default parser.
        
        Args:
            document: Document to parse
            parser_name: Name of parser to use (defaults to configured default)
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If parser is not found or document format is unsupported
        """
        raise NotImplementedError
    
    def get_available_parsers(self) -> list[str]:
        """Get list of available parser names.
        
        Returns:
            List of available parser names
        """
        raise NotImplementedError
    
    def _get_parser(self, parser_name: str) -> ParserInterface:
        """Get parser instance (with caching).
        
        Args:
            parser_name: Name of parser
            
        Returns:
            ParserInterface instance
        """
        raise NotImplementedError
