"""Chandra OCR parser implementation."""
from typing import List, Optional

from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult, Block


class ChandraParser(BaseParser):
    """Parser using Chandra OCR model."""
    
    _inference_manager = None
    _model_loaded = False
    _parse_markdown = None
    
    def __init__(self, config=None):
        """Initialize Chandra parser.
        
        Args:
            config: Parser configuration
        """
        super().__init__(config)
        self._ensure_model_loaded()
    
    def get_name(self) -> str:
        """Get parser name."""
        return "chandra"
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [
            'pdf',  # PDF
            'png', 'jpeg', 'jpg', 'webp', 'gif', 'tiff',  # Images
        ]
    
    @classmethod
    def _ensure_model_loaded(cls):
        """Load Chandra model on GPU (singleton pattern).
        
        Note:
            - Model is loaded once and reused
            - Requires GPU environment
        """
        if cls._model_loaded:
            return
        
        # Check GPU availability
        try:
            import torch
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "Chandra parser requires GPU. CUDA is not available."
                )
        except ImportError:
            raise ImportError(
                "PyTorch is not installed. Install it with: pip install torch"
            )
        
        try:
            from chandra.model import InferenceManager
            from chandra.output import parse_markdown
            
            import torch
            
            # Use InferenceManager as per Hugging Face documentation
            # https://huggingface.co/datalab-to/chandra
            # This handles model loading and generation internally
            cls._inference_manager = InferenceManager(method="hf")
            cls._parse_markdown = parse_markdown
            
            cls._model_loaded = True
        except ImportError as e:
            raise ImportError(
                f"Chandra dependencies not installed. "
                f"Install with: pip install chandra-ocr transformers torch. "
                f"Error: {str(e)}"
            )
    
    def _load_image(self, file_path: str, page_number: int = 0):
        """Load image from file path.
        
        Args:
            file_path: Path to image file or PDF
            page_number: Page number for PDF (0-indexed)
            
        Returns:
            PIL Image object
        """
        from PIL import Image
        
        if file_path.endswith('.pdf'):
            # Convert PDF page to image
            try:
                from pdf2image import convert_from_path
                
                images = convert_from_path(file_path)
                if page_number < len(images):
                    return images[page_number]
                else:
                    raise ValueError(
                        f"Page {page_number} not found. PDF has {len(images)} page(s)"
                    )
            except ImportError:
                raise ImportError(
                    "pdf2image is not installed. Install it with: pip install pdf2image"
                )
            except Exception as e:
                raise ValueError(f"Failed to convert PDF to image: {str(e)}")
        
        return Image.open(file_path)
    
    def _do_parse(self, document: Document) -> ParseResult:
        """Parse document using Chandra OCR model.
        
        Args:
            document: Document to parse (page-level, page 0)
            
        Returns:
            ParseResult containing parsed data
        """
        from chandra.model.schema import BatchInputItem
        
        # Load image (page-level: always page 0)
        image = self._load_image(document.file_path, page_number=0)
        
        # Prepare batch
        batch = [BatchInputItem(image=image, prompt_type="ocr_layout")]
        
        # Generate result using InferenceManager
        # This follows the Hugging Face documentation example
        result = ChandraParser._inference_manager.generate(batch)[0]
        
        # Parse markdown
        markdown = ChandraParser._parse_markdown(result.raw)
        
        # Generate full content (Upstage style)
        import re
        full_content = {
            "html": markdown,  # Chandra markdown contains HTML
            "markdown": markdown,
            "text": re.sub(r'<[^>]+>', '', markdown)  # Remove HTML tags for text
        }
        
        # Convert to blocks
        blocks = []
        element_id = 0
        
        # Extract HTML tables if present
        html_tables = re.findall(r'<table.*?</table>', markdown, re.DOTALL | re.IGNORECASE)
        
        if html_tables:
            # Add tables as separate blocks
            for table_html in html_tables:
                # Extract text from HTML table
                table_text = re.sub(r'<[^>]+>', '', table_html).strip()
                # Simple markdown conversion
                table_md = table_text.replace('\n', ' | ').strip()
                
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
                            "parser": "chandra",
                            "file_type": document.file_type,
                            "format": "markdown",
                        },
                    )
                )
                element_id += 1
            
            # Add remaining text (remove tables)
            text_content = markdown
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
                        metadata={
                            "parser": "chandra",
                            "file_type": document.file_type,
                        },
                    )
                )
                element_id += 1
        else:
            # No tables, add as single text block
            blocks.append(
                Block(
                    type="text",
                    text=markdown,
                    page=1,
                    element_id=element_id,
                    content={
                        "html": markdown,
                        "markdown": markdown,
                        "text": re.sub(r'<[^>]+>', '', markdown)
                    },
                    metadata={
                        "parser": "chandra",
                        "file_type": document.file_type,
                        "format": "markdown",
                    },
                )
            )
            element_id += 1
        
        return ParseResult(
            document_id=document.id,
            blocks=blocks,
            full_content=full_content,
            usage={"pages": 1},
            metadata={
                "parser": self.get_name(),
                "file_type": document.file_type,
                "format": "markdown",
            },
        )
