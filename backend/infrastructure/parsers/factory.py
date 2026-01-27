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
        if parser_name not in cls._parsers:
            available = ", ".join(cls._parsers.keys()) if cls._parsers else "none"
            raise ValueError(
                f"Unknown parser: {parser_name}. "
                f"Available parsers: {available}"
            )
        
        parser_class = cls._parsers[parser_name]
        return parser_class(config=config)
    
    @classmethod
    def register(cls, name: str, parser_class: Type[ParserInterface]):
        """Register a new parser class.
        
        Args:
            name: Parser identifier name
            parser_class: Parser class implementing ParserInterface
        """
        cls._parsers[name] = parser_class
    
    @classmethod
    def list_available(cls) -> List[str]:
        """Get list of available parser names.
        
        Returns:
            List of registered parser names
        """
        return list(cls._parsers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if parser is registered.
        
        Args:
            name: Parser name to check
            
        Returns:
            True if parser is registered
        """
        return name in cls._parsers
