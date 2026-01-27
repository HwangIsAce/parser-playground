"""Parser implementations."""
from infrastructure.parsers.factory import ParserFactory
from infrastructure.parsers.unstructured_parser import UnstructuredParser

# Register default parsers
ParserFactory.register("unstructured", UnstructuredParser)

__all__ = ["ParserFactory", "UnstructuredParser"]
