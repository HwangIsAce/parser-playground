"""Docling parser implementation."""
from typing import List

from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult, Block


class DoclingParser(BaseParser):
    """Parser using Docling library."""
    
    def __init__(self, config=None):
        """Initialize Docling parser.
        
        Args:
            config: Parser configuration
        """
        super().__init__(config)
        self._converter = None
    
    def get_name(self) -> str:
        """Get parser name."""
        return "docling"
    
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
    
    def _get_converter(self):
        """Get or create Docling converter (lazy loading)."""
        if self._converter is None:
            try:
                from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
                from docling.datamodel.pipeline_options import PdfPipelineOptions
                from docling.datamodel.base_models import InputFormat
                
                # Get config from settings or instance config
                config = self.config or {}
                
                # Configure pipeline options with enrichments
                # Enable remote services if needed (for remote vision models)
                enable_remote = config.get("enable_remote_services", False)
                pipeline_options = PdfPipelineOptions(enable_remote_services=enable_remote)
                
                # Enable OCR (important for image files to extract text)
                pipeline_options.do_ocr = config.get("do_ocr", True)
                
                # Enable picture images and OCR (important for image files)
                pipeline_options.generate_picture_images = config.get("generate_picture_images", True)
                pipeline_options.images_scale = config.get("images_scale", 2)
                
                # Enable table structure recognition (important for table extraction)
                pipeline_options.do_table_structure = config.get("do_table_structure", True)
                
                # Table structure options
                if hasattr(pipeline_options, 'table_structure_options'):
                    table_config = config.get("table_structure_options", {})
                    if table_config.get("do_cell_matching") is not None:
                        pipeline_options.table_structure_options.do_cell_matching = table_config.get("do_cell_matching", True)
                
                # Enable enrichments based on config
                pipeline_options.do_picture_description = config.get("do_picture_description", True)
                pipeline_options.do_picture_classification = config.get("do_picture_classification", False)
                pipeline_options.do_code_enrichment = config.get("do_code_enrichment", False)
                pipeline_options.do_formula_enrichment = config.get("do_formula_enrichment", False)
                
                # Create format options with pipeline options
                pdf_format_option = PdfFormatOption(pipeline_options=pipeline_options)
                image_format_option = ImageFormatOption(pipeline_options=pipeline_options)
                
                # Create converter with options for both PDF and IMAGE formats
                self._converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: pdf_format_option,
                        InputFormat.IMAGE: image_format_option,
                    }
                )
            except ImportError:
                raise ImportError(
                    "Docling is not installed. Install it with: pip install docling"
                )
        return self._converter
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using Docling library.
        
        Args:
            document: Document to parse
            
        Returns:
            ParseResult containing parsed data
        """
        converter = self._get_converter()
        
        # Convert document
        result = converter.convert(document.file_path)
        
        # Convert DoclingDocument to ParseResult
        blocks = []
        doc = result.document
        element_id = 0
        
        # Generate full content (Upstage style)
        full_content = {
            "html": doc.export_to_html(),
            "markdown": doc.export_to_markdown(),
            "text": doc.export_to_text()
        }
        
        # Try to extract structured content from pages
        # DoclingDocument.pages is a dict with page numbers as keys
        for page_no, page in doc.pages.items():
            # Process page items if available
            if hasattr(page, 'items'):
                for item in page.items:
                    item_type = type(item).__name__
                    
                    # Generate coordinates from bbox if available
                    coordinates = None
                    if hasattr(item, 'bbox') and item.bbox:
                        # Normalize coordinates (assuming page size)
                        page_size = page.size if hasattr(page, 'size') else None
                        if page_size:
                            l = item.bbox.l / page_size.width
                            t = item.bbox.t / page_size.height
                            r = item.bbox.r / page_size.width
                            b = item.bbox.b / page_size.height
                        else:
                            l, t, r, b = item.bbox.l, item.bbox.t, item.bbox.r, item.bbox.b
                        
                        coordinates = [
                            {"x": l, "y": t},  # 좌상단
                            {"x": r, "y": t},  # 우상단
                            {"x": r, "y": b},  # 우하단
                            {"x": l, "y": b}   # 좌하단
                        ]
                    
                    # Check if it's a table item
                    if hasattr(item, 'label') and 'table' in str(item.label).lower():
                        # Extract table content
                        try:
                            table_md = item.export_to_markdown() if hasattr(item, 'export_to_markdown') else str(item)
                            table_html = item.export_to_html() if hasattr(item, 'export_to_html') else None
                            
                            content = {
                                "markdown": table_md,
                                "text": table_md
                            }
                            if table_html:
                                content["html"] = table_html
                            
                            blocks.append(
                                Block(
                                    type="table",
                                    text=table_md,
                                    coordinates=coordinates,
                                    page=page_no,
                                    element_id=element_id,
                                    content=content,
                                    metadata={
                                        "parser": "docling",
                                        "file_type": document.file_type,
                                        "item_type": item_type,
                                    },
                                )
                            )
                            element_id += 1
                        except Exception:
                            # Fallback to string representation
                            blocks.append(
                                Block(
                                    type="table",
                                    text=str(item),
                                    coordinates=coordinates,
                                    page=page_no,
                                    element_id=element_id,
                                    metadata={
                                        "parser": "docling",
                                        "file_type": document.file_type,
                                        "item_type": item_type,
                                    },
                                )
                            )
                            element_id += 1
                    else:
                        # Extract text content
                        try:
                            if hasattr(item, 'export_to_markdown'):
                                text_content = item.export_to_markdown()
                                text_html = item.export_to_html() if hasattr(item, 'export_to_html') else None
                            elif hasattr(item, 'text'):
                                text_content = item.text
                                text_html = None
                            else:
                                text_content = str(item)
                                text_html = None
                            
                            if text_content and text_content.strip():
                                content = {
                                    "markdown": text_content,
                                    "text": text_content
                                }
                                if text_html:
                                    content["html"] = text_html
                                
                                blocks.append(
                                    Block(
                                        type="text",
                                        text=text_content,
                                        coordinates=coordinates,
                                        page=page_no,
                                        element_id=element_id,
                                        content=content if content.get("html") else None,
                                        metadata={
                                            "parser": "docling",
                                            "file_type": document.file_type,
                                            "item_type": item_type,
                                        },
                                    )
                                )
                                element_id += 1
                        except Exception:
                            # Fallback: skip this item
                            pass
        
        # If no blocks were created, try HTML export and parse tables from it
        if not blocks:
            # Try HTML export which may contain more structure
            html_content = doc.export_to_html()
            
            # Extract tables from HTML if present
            import re
            html_tables = re.findall(r'<table.*?</table>', html_content, re.DOTALL | re.IGNORECASE)
            
            if html_tables:
                # Add tables as separate blocks
                for i, table_html in enumerate(html_tables):
                    # Extract text from HTML table
                    table_text = re.sub(r'<[^>]+>', '', table_html).strip()
                    table_md = table_text  # Simple conversion
                    
                    blocks.append(
                        Block(
                            type="table",
                            text=table_md,
                            page=1,
                            element_id=element_id,
                            content={
                                "html": table_html,
                                "markdown": table_md,
                                "text": table_text
                            },
                            metadata={
                                "parser": "docling",
                                "file_type": document.file_type,
                                "format": "html",
                                "table_index": i,
                            },
                        )
                    )
                    element_id += 1
                
                # Add remaining HTML content as text (remove tables)
                text_html = html_content
                for table in html_tables:
                    text_html = text_html.replace(table, "")
                if text_html.strip():
                    text_content = re.sub(r'<[^>]+>', '', text_html).strip()
                    blocks.append(
                        Block(
                            type="text",
                            text=text_content,
                            page=1,
                            element_id=element_id,
                            content={
                                "html": text_html,
                                "text": text_content
                            },
                            metadata={
                                "parser": "docling",
                                "file_type": document.file_type,
                                "format": "html",
                            },
                        )
                    )
                    element_id += 1
            else:
                # Fallback to markdown export
                markdown_content = doc.export_to_markdown()
                blocks.append(
                    Block(
                        type="text",
                        text=markdown_content,
                        page=1,
                        element_id=element_id,
                        metadata={
                            "parser": "docling",
                            "file_type": document.file_type,
                        },
                    )
                )
                element_id += 1
        
        return ParseResult(
            document_id=document.id,
            blocks=blocks,
            full_content=full_content,
            usage={"pages": doc.num_pages()},
            metadata={
                "parser": self.get_name(),
                "file_type": document.file_type,
                "format": "markdown",
            },
        )
