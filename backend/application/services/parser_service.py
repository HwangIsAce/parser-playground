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
    Supports page-level parsing with mode selection (basic/enhance).
    """
    
    def __init__(self):
        """Initialize parser service.
        
        Note:
            - Maps mode to parser names
            - basic -> docling
            - enhance -> chandra
        """
        self.mode_mapping = {
            "basic": "docling",
            "enhance": "chandra",
        }
        self.default_mode = getattr(settings, 'DEFAULT_PARSE_MODE', 'basic')
        self._parser_cache: Dict[str, ParserInterface] = {}
    
    def parse_document(
        self,
        document: Document,
        mode: str = "basic"
    ) -> ParseResult:
        """Parse a document (page) using specified mode.
        
        Args:
            document: Document entity (single page) to parse
            mode: Parse mode ('basic' for Docling, 'enhance' for Chandra)
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If mode is invalid or parser is not found
            
        Note:
            - Currently processes single page only
            - Future: Can be extended for multi-page document parsing
        """
        # Map mode to parser name
        parser_name = self.mode_mapping.get(mode)
        if not parser_name:
            raise ValueError(
                f"Unknown mode: {mode}. Use 'basic' or 'enhance'"
            )
        
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
        """
        return ParserFactory.list_available()
    
    def get_available_modes(self) -> list[str]:
        """Get list of available parse modes.
        
        Returns:
            List of available modes ['basic', 'enhance']
        """
        return list(self.mode_mapping.keys())
    
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
