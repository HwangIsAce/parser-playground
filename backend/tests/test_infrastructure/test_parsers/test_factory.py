"""Tests for ParserFactory."""
import pytest

from infrastructure.parsers.factory import ParserFactory
from infrastructure.parsers.unstructured_parser import UnstructuredParser
from core.interfaces.parser_interface import ParserInterface


class TestParserFactory:
    """Test ParserFactory."""
    
    def test_register_parser(self):
        """Test parser registration."""
        class TestParser(ParserInterface):
            def get_name(self):
                return "test_parser"
            def get_supported_formats(self):
                return ["pdf"]
            def parse(self, document):
                pass
        
        ParserFactory.register("test_parser", TestParser)
        assert ParserFactory.is_registered("test_parser") is True
    
    def test_create_parser(self):
        """Test parser creation."""
        # UnstructuredParser should be registered in __init__.py
        parser = ParserFactory.create("unstructured")
        assert isinstance(parser, UnstructuredParser)
    
    def test_create_parser_with_config(self):
        """Test parser creation with config."""
        config = {"key": "value"}
        parser = ParserFactory.create("unstructured", config=config)
        assert parser.config == config
    
    def test_create_unregistered_parser_raises_error(self):
        """Test creating unregistered parser raises error."""
        with pytest.raises(ValueError, match="Unknown parser"):
            ParserFactory.create("nonexistent_parser")
    
    def test_list_available_parsers(self):
        """Test listing available parsers."""
        parsers = ParserFactory.list_available()
        assert isinstance(parsers, list)
        assert "unstructured" in parsers
    
    def test_is_registered(self):
        """Test checking if parser is registered."""
        assert ParserFactory.is_registered("unstructured") is True
        assert ParserFactory.is_registered("nonexistent") is False
