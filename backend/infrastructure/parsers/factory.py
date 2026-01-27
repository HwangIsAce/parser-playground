"""Parser factory for creating parser instances."""
from typing import Dict, Type, List

from core.interfaces.parser_interface import ParserInterface


class ParserFactory:
    """Factory for creating parser instances."""
    
    _parsers: Dict[str, Type[ParserInterface]] = {}
    
    @classmethod
    def create(cls, parser_name: str, config: Dict = None) -> ParserInterface:
        """Create a parser instance.
        
        Args:
            parser_name: Name of the parser to create
            config: Optional configuration dictionary
            
        Returns:
            ParserInterface instance
            
        Raises:
            ValueError: If parser name is not registered
        """
        raise NotImplementedError
    
    @classmethod
    def register(cls, name: str, parser_class: Type[ParserInterface]):
        """Register a new parser class.
        
        Args:
            name: Parser identifier name
            parser_class: Parser class implementing ParserInterface
        """
        pass
    
    @classmethod
    def list_available(cls) -> List[str]:
        """Get list of available parser names.
        
        Returns:
            List of registered parser names
        """
        raise NotImplementedError
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if parser is registered.
        
        Args:
            name: Parser name to check
            
        Returns:
            True if parser is registered
        """
        raise NotImplementedError
