"""Chandra OCR parser implementation."""
from typing import List, Optional

from infrastructure.parsers.base import BaseParser
from core.models.document import Document
from core.models.parse_result import ParseResult, Block


class ChandraParser(BaseParser):
    """Parser using Chandra OCR model."""
    
    _model = None
    _processor = None
    _model_loaded = False
    _generate_hf = None
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
            from transformers import AutoModel, AutoProcessor
            from chandra.model.hf import generate_hf
            from chandra.output import parse_markdown
            
            import torch
            
            # Load model and processor
            cls._model = AutoModel.from_pretrained(
                "datalab-to/chandra",
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            cls._processor = AutoProcessor.from_pretrained("datalab-to/chandra")
            
            # Store utility functions
            cls._generate_hf = generate_hf
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
        
        # Generate result
        result = self._generate_hf(batch, self._model)[0]
        
        # Parse markdown
        markdown = self._parse_markdown(result.raw)
        
        # Convert to blocks
        blocks = [
            Block(
                type="text",
                text=markdown,
                metadata={
                    "parser": "chandra",
                    "file_type": document.file_type,
                    "format": "markdown",
                },
            )
        ]
        
        return ParseResult(
            document_id=document.id,
            blocks=blocks,
            metadata={
                "parser": self.get_name(),
                "file_type": document.file_type,
                "format": "markdown",
            },
        )
