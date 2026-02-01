"""Remote Docling parser implementation via API."""
from typing import List

from infrastructure.parsers.base import BaseParser
from infrastructure.clients.parser_api_client import ParserAPIClient
from infrastructure.storage.file_storage import FileStorage
from core.models.document import Document
from core.models.parse_result import ParseResult, Block
from config import settings


class RemoteDoclingParser(BaseParser):
    """Remote Docling parser via API.
    
    This parser calls the remote Docling API endpoint (/v1/documents/process)
    instead of running Docling locally.
    """
    
    def __init__(self, config=None):
        """Initialize remote Docling parser.
        
        Args:
            config: Parser configuration (optional, uses settings if not provided)
        """
        super().__init__(config)
        self.client = ParserAPIClient(
            base_url=settings.PARSER_API_BASE_URL,
            timeout=settings.PARSER_API_TIMEOUT,
            retry_count=settings.PARSER_API_RETRY_COUNT,
            retry_delay=getattr(settings, 'PARSER_API_RETRY_DELAY', 1.0)
        )
        self.storage = FileStorage()
    
    def get_name(self) -> str:
        """Get parser name."""
        return "docling-remote"
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [
            'pdf', 'doc', 'docx', 'odt',  # Documents
            'xls', 'xlsx', 'ods',  # Spreadsheets
            'ppt', 'pptx', 'odp',  # Presentations
            'html', 'epub',  # Web & Books
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',  # Images
            'wav', 'mp3', 'vtt',  # Audio/Video
        ]
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using remote Docling API.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If parsing fails
        """
        # Load file content
        file_content = self.storage.load(document.file_path)
        
        # Call remote API
        try:
            api_response = self.client.process_document(
                document.file_path,
                file_content
            )
        except Exception as e:
            raise ValueError(f"Failed to call remote Docling API: {str(e)}")
        
        # Convert API response to ParseResult
        return self._convert_api_response(api_response, document)
    
    def _convert_api_response(
        self,
        api_response: dict,
        document: Document
    ) -> ParseResult:
        """Convert API response to ParseResult.
        
        Args:
            api_response: API response dict with keys: id, text, metadata, structure
            document: Original document entity
            
        Returns:
            ParseResult containing parsed data
        """
        # Extract data from API response
        text = api_response.get("text", "")
        metadata = api_response.get("metadata", {})
        structure = api_response.get("structure", {})
        api_id = api_response.get("id", "")
        
        # Create blocks from text
        blocks = []
        element_id = 0
        
        if text:
            # Create a single text block with the extracted text
            blocks.append(
                Block(
                    type="text",
                    text=text,
                    page=1,
                    element_id=element_id,
                    metadata={
                        "parser": "docling-remote",
                        "file_type": document.file_type,
                        "api_id": api_id,
                    }
                )
            )
            element_id += 1
        
        # Add structure info if available (sections, etc.)
        if structure.get("sections"):
            # Could parse sections into separate blocks if needed
            # For now, structure info is stored in metadata
            pass
        
        # Generate full content
        full_content = {
            "text": text,
            "markdown": text,  # API doesn't provide markdown, use text
            "html": f"<div>{text}</div>"  # Simple HTML wrapper
        }
        
        return ParseResult(
            document_id=document.id,
            blocks=blocks,
            full_content=full_content,
            usage={"pages": metadata.get("page_count", 1)},
            metadata={
                "parser": self.get_name(),
                "file_type": document.file_type,
                "api_id": api_id,
                "api_metadata": metadata,
                "structure": structure,
            }
        )
