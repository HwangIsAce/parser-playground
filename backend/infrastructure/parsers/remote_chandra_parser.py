"""Remote Chandra OCR parser implementation via API."""
from typing import List
import re
import io

from infrastructure.parsers.base import BaseParser
from infrastructure.clients.parser_api_client import ParserAPIClient
from infrastructure.storage.file_storage import FileStorage
from core.models.document import Document
from core.models.parse_result import ParseResult, Block
from config import settings


class RemoteChandraParser(BaseParser):
    """Remote Chandra OCR parser via API.
    
    This parser calls the remote Chandra API endpoint (/v1/ocr)
    instead of running Chandra locally. For PDF files, it converts
    them to images before sending to the API.
    """
    
    def __init__(self, config=None):
        """Initialize remote Chandra parser.
        
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
        return "chandra-remote"
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [
            'pdf',  # PDF (will be converted to image)
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',  # Images
        ]
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using remote Chandra OCR API.
        
        Args:
            document: Document to parse (page-level, page 0)
            
        Returns:
            ParseResult containing parsed data
            
        Raises:
            ValueError: If parsing fails
        """
        # Load file content (convert PDF to image if needed)
        file_content, filename = self._prepare_file_content(document)
        
        # Call remote API — request HTML so we get <table> for column layout
        try:
            api_response = self.client.process_ocr(
                filename,
                file_content,
                prompt_type="ocr_layout",
                output_format="html"
            )
        except Exception as e:
            raise ValueError(f"Failed to call remote Chandra API: {str(e)}")
        
        # Convert API response to ParseResult
        return self._convert_api_response(api_response, document)
    
    def _prepare_file_content(self, document: Document) -> tuple[bytes, str]:
        """Prepare file content for API call.
        
        For PDF files, converts to image. For image files, loads directly.
        
        Args:
            document: Document entity
            
        Returns:
            Tuple of (file_content: bytes, filename: str)
            
        Raises:
            ValueError: If file conversion fails
        """
        file_type = document.file_type.lower()
        
        if file_type == 'pdf':
            # Convert PDF to image
            try:
                from pdf2image import convert_from_path
                from PIL import Image
                
                # Convert PDF page to image (page 0)
                images = convert_from_path(document.file_path)
                if not images:
                    raise ValueError("Failed to convert PDF: no pages found")
                
                # Get first page
                image = images[0]
                
                # Convert PIL Image to bytes (PNG format)
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                file_content = img_bytes.getvalue()
                
                # Use PNG extension for filename
                filename = document.filename.rsplit('.', 1)[0] + '.png'
                
                return file_content, filename
                
            except ImportError:
                raise ValueError(
                    "pdf2image is not installed. "
                    "Install it with: pip install pdf2image"
                )
            except Exception as e:
                raise ValueError(f"Failed to convert PDF to image: {str(e)}")
        
        else:
            # Image file - load directly
            file_content = self.storage.load(document.file_path)
            filename = document.filename
            return file_content, filename
    
    @staticmethod
    def _markdown_tables_to_html(markdown: str) -> List[str]:
        """Convert markdown pipe tables to HTML table strings.
        
        Returns list of HTML <table>...</table> strings (empty if none found).
        """
        def escape(s: str) -> str:
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        lines = markdown.splitlines()
        tables_html: List[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith("|") and line.strip().endswith("|"):
                table_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                rows = []
                for j, row_line in enumerate(table_lines):
                    cells = [c.strip() for c in row_line.strip().strip("|").split("|")]
                    if not cells:
                        continue
                    if j == 1 and all(re.match(r"^[-:]+$", c) for c in cells):
                        continue
                    is_header = j == 0
                    tag = "th" if is_header else "td"
                    rows.append(f"<tr>{''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells)}</tr>")
                if rows:
                    tables_html.append(f"<table><tbody>{''.join(rows)}</tbody></table>")
                continue
            i += 1
        return tables_html

    def _convert_api_response(
        self,
        api_response: dict,
        document: Document
    ) -> ParseResult:
        """Convert API response to ParseResult.
        
        Args:
            api_response: API response dict with keys: id, text, markdown, html, json, metadata
            document: Original document entity
            
        Returns:
            ParseResult containing parsed data
        """
        # Extract data from API response (API may return json: null)
        text = api_response.get("text", "")
        markdown = api_response.get("markdown", "")
        html = api_response.get("html", "")
        json_data = api_response.get("json") or {}
        metadata = api_response.get("metadata") or {}
        api_id = api_response.get("id", "")
        
        # Generate full content
        full_content = {
            "text": text,
            "markdown": markdown if markdown else text,
            "html": html if html else f"<div>{text}</div>"
        }
        
        # Convert to blocks
        blocks = []
        element_id = 0
        
        # If JSON blocks are available, use them
        if json_data.get("blocks"):
            for block_data in json_data["blocks"]:
                blocks.append(
                    Block(
                        type=block_data.get("type", "text"),
                        text=block_data.get("text", ""),
                        page=1,
                        element_id=element_id,
                        content={
                            "html": block_data.get("html", ""),
                            "markdown": block_data.get("markdown", ""),
                            "text": block_data.get("text", "")
                        },
                        metadata={
                            "parser": "chandra-remote",
                            "file_type": document.file_type,
                            "api_id": api_id,
                        }
                    )
                )
                element_id += 1
        
        # Otherwise, parse markdown/HTML
        if not blocks:
            # Use HTML if available, otherwise markdown
            content_to_parse = html if html else markdown
            
            # Extract HTML tables if present
            html_tables = re.findall(
                r'<table.*?</table>',
                content_to_parse,
                re.DOTALL | re.IGNORECASE
            )
            
            # If no HTML tables but we have markdown, try markdown pipe tables
            if not html_tables and markdown:
                html_tables = self._markdown_tables_to_html(markdown)
            
            if html_tables:
                # Add tables as separate blocks
                for table_html in html_tables:
                    table_text = re.sub(r'<[^>]+>', '', table_html).strip()
                    blocks.append(
                        Block(
                            type="table",
                            text=table_text,
                            page=1,
                            element_id=element_id,
                            content={
                                "html": table_html,
                                "markdown": table_text,
                                "text": table_text
                            },
                            metadata={
                                "parser": "chandra-remote",
                                "file_type": document.file_type,
                                "api_id": api_id,
                            }
                        )
                    )
                    element_id += 1
                
                # Add remaining text (remove tables)
                text_content = content_to_parse
                for table in html_tables:
                    text_content = text_content.replace(table, "")
                text_content = re.sub(r'<[^>]+>', '', text_content).strip()
                
                if text_content:
                    blocks.append(
                        Block(
                            type="text",
                            text=text_content,
                            page=1,
                            element_id=element_id,
                            content={
                                "html": text_content,
                                "markdown": text_content,
                                "text": text_content
                            },
                            metadata={
                                "parser": "chandra-remote",
                                "file_type": document.file_type,
                                "api_id": api_id,
                            }
                        )
                    )
                    element_id += 1
            else:
                # Single text block — no <table> or markdown pipe table from API; keep as text.
                # Table layout should come from the parser API (HTML/JSON) to match original columns.
                content_text = text if text else (markdown if markdown else "")
                blocks.append(
                    Block(
                        type="text",
                        text=content_text,
                        page=1,
                        element_id=element_id,
                        content=full_content,
                        metadata={
                            "parser": "chandra-remote",
                            "file_type": document.file_type,
                            "api_id": api_id,
                        }
                    )
                )
                element_id += 1
        
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
            }
        )
