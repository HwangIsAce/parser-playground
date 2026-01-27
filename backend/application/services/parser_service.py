"""Parser service for document parsing orchestration."""
from typing import Dict, Optional

from core.models.document import Document
from core.models.parse_result import ParseResult
from core.interfaces.parser_interface import ParserInterface
from infrastructure.parsers import ParserFactory
from config import settings


class ParserService:
    """Service for document parsing operations.
    
    Note: Orchestrates parsing operations using registered parsers.
    Supports page-level parsing (single page per document).
    """
    
    def __init__(self):
        """Initialize parser service.
        
        Note:
            - Loads default parser name from settings
            - Initializes parser instance cache
            - Parser registration happens when importing infrastructure.parsers
        """
        self.default_parser_name = settings.DEFAULT_PARSER
        self._parser_cache: Dict[str, ParserInterface] = {}
    
    def parse_document(
        self,
        document: Document,
        parser_name: Optional[str] = None
    ) -> ParseResult:
        """Parse a document (page) using specified or default parser.
        
        Args:
            document: Document entity (single page) to parse
            parser_name: Name of parser to use (defaults to configured default)
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If parser is not found or document format is unsupported
            
        Note:
            - Currently processes single page only
            - Future: Can be extended for multi-page document parsing
        """
        # Determine parser name (use specified or default)
        parser_name = parser_name or self.default_parser_name
        
        # Get parser instance (with caching)
        parser = self._get_parser(parser_name)
        
        # Parse document
        try:
            parse_result = parser.parse(document)
            return parse_result
        except ValueError as e:
            # Re-raise parser-level errors
            raise ValueError(f"Failed to parse document: {str(e)}")
    
    def get_available_parsers(self) -> list[str]:
        """Get list of available parser names.
        
        Returns:
            List of registered parser names
            
        Examples:
            ["unstructured", "upstage"]  # Registered parsers
        """
        return ParserFactory.list_available()
    
    def _get_parser(self, parser_name: str) -> ParserInterface:
        """Get parser instance (with caching).
        
        Args:
            parser_name: Name of parser
            
        Returns:
            ParserInterface instance
            
        Note:
            - Caches parser instances for performance
            - Same parser is reused across multiple parse operations
            - Loads parser-specific config from settings
        """
        # Create parser if not in cache
        if parser_name not in self._parser_cache:
            # Get parser-specific config from settings
            parser_config = settings.PARSER_CONFIGS.get(parser_name, {})
            
            # Create parser instance via Factory
            self._parser_cache[parser_name] = ParserFactory.create(
                parser_name,
                config=parser_config
            )
        
        # Return cached parser instance
        return self._parser_cache[parser_name]
