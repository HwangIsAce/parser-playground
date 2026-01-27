"""Base parser with common functionality."""
from typing import Dict, Any
from abc import abstractmethod

from core.interfaces.parser_interface import ParserInterface
from core.models.document import Document
from core.models.parse_result import ParseResult


class BaseParser(ParserInterface):
    """Base class for all parsers with common functionality."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize parser with configuration.
        
        Args:
            config: Parser-specific configuration dictionary
        """
        self.config = config or {}
    
    def validate_document(self, document: Document) -> bool:
        """Validate if document format is supported.
        
        Args:
            document: Document to validate
            
        Returns:
            True if document format is supported
        """
        supported_formats = [fmt.lower() for fmt in self.get_supported_formats()]
        return document.file_type.lower() in supported_formats
    
    def preprocess(self, document: Document) -> Document:
        """Preprocess document before parsing (can be overridden).
        
        Args:
            document: Document to preprocess
            
        Returns:
            Preprocessed document
        """
        return document
    
    def parse(self, document: Document) -> ParseResult:
        """Template method for parsing.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If document format is not supported
        """
        if not self.validate_document(document):
            raise ValueError(
                f"Unsupported format: {document.file_type}. "
                f"Supported formats: {self.get_supported_formats()}"
            )
        
        processed_doc = self.preprocess(document)
        return self._do_parse(processed_doc)
    
    @abstractmethod
    def _do_parse(self, document: Document) -> ParseResult:
        """Actual parsing logic (implemented by subclasses).
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
        """
        pass
