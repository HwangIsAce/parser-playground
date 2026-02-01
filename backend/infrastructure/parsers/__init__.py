"""Parser implementations."""
from infrastructure.parsers.factory import ParserFactory
from infrastructure.parsers.unstructured_parser import UnstructuredParser

# Register default parsers
ParserFactory.register("unstructured", UnstructuredParser)

# Register Docling parser (if available)
try:
    from infrastructure.parsers.docling_parser import DoclingParser
    ParserFactory.register("docling", DoclingParser)
except ImportError:
    # Docling not installed, skip registration
    pass

# Register Chandra parser (if available)
try:
    from infrastructure.parsers.chandra_parser import ChandraParser
    ParserFactory.register("chandra", ChandraParser)
except (ImportError, RuntimeError) as e:
    # Chandra not installed or GPU not available, skip registration
    pass

# Register Remote parsers (if enabled)
from config import settings
if settings.PARSER_API_ENABLED:
    try:
        from infrastructure.parsers.remote_docling_parser import RemoteDoclingParser
        from infrastructure.parsers.remote_chandra_parser import RemoteChandraParser
        ParserFactory.register("docling-remote", RemoteDoclingParser)
        ParserFactory.register("chandra-remote", RemoteChandraParser)
    except ImportError as e:
        # Remote parser dependencies not available, skip registration
        pass

__all__ = ["ParserFactory", "UnstructuredParser"]
