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
        """Load Chandra model on GPU (singleton pattern with multi-worker support).
        
        Note:
            - Model is loaded once per process and reused
            - Uses file locking to prevent multiple processes from loading simultaneously
            - Checks GPU memory to ensure sufficient space before loading
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
        
        # Use file lock to prevent multiple processes from loading model simultaneously
        import tempfile
        import time
        import os
        
        # Try to import fcntl (Unix/Linux only)
        try:
            import fcntl
            HAS_FCNTL = True
        except ImportError:
            HAS_FCNTL = False
        
        lock_file_path = tempfile.gettempdir() + "/chandra_model_load.lock"
        max_wait_time = 300  # Maximum wait time: 5 minutes
        wait_interval = 2  # Check every 2 seconds
        required_memory_gb = 16.0  # Model requires ~13-16GB
        
        lock_file = None
        try:
            if HAS_FCNTL:
                # Use fcntl for proper file locking (Unix/Linux)
                lock_file = open(lock_file_path, 'w')
                start_time = time.time()
                
                while True:
                    try:
                        # Try to acquire exclusive lock (non-blocking)
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break  # Lock acquired successfully
                    except BlockingIOError:
                        # Lock is held by another process, wait and retry
                        elapsed = time.time() - start_time
                        if elapsed > max_wait_time:
                            raise RuntimeError(
                                f"Timeout waiting for model lock. Another process is loading the model. "
                                f"Waited {elapsed:.0f} seconds."
                            )
                        time.sleep(wait_interval)
                        # Reopen lock file in case it was deleted
                        lock_file.close()
                        lock_file = open(lock_file_path, 'w')
            else:
                # Fallback: Use simple file existence check (less reliable but works on Windows)
                start_time = time.time()
                while os.path.exists(lock_file_path):
                    elapsed = time.time() - start_time
                    if elapsed > max_wait_time:
                        raise RuntimeError(
                            f"Timeout waiting for model lock. Another process is loading the model. "
                            f"Waited {elapsed:.0f} seconds."
                        )
                    time.sleep(wait_interval)
                # Create lock file
                lock_file = open(lock_file_path, 'w')
                lock_file.write(str(os.getpid()))
                lock_file.flush()
                os.fsync(lock_file.fileno())
            
            # Lock acquired, check if model is already loaded (double-check)
            if cls._model_loaded:
                return
            
            # Check available GPU memory before loading model
            # Use nvidia-smi for more accurate memory check across all processes
            import subprocess
            try:
                # Get GPU memory info from nvidia-smi (more accurate than PyTorch)
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Parse output: "used, total"
                    parts = result.stdout.strip().split(', ')
                    if len(parts) == 2:
                        used_memory_mb = int(parts[0])
                        total_memory_mb = int(parts[1])
                        free_memory_gb = (total_memory_mb - used_memory_mb) / 1024.0
                        total_memory_gb = total_memory_mb / 1024.0
                        
                        # More conservative: require 18GB free (model needs ~16GB + buffer)
                        if free_memory_gb < 18.0:
                            raise RuntimeError(
                                f"Insufficient GPU memory. Required: 18.0GB free, "
                                f"Available: {free_memory_gb:.1f}GB. "
                                f"Total: {total_memory_gb:.1f}GB, "
                                f"Used: {used_memory_mb / 1024.0:.1f}GB. "
                                f"Please wait for other workers to finish or reduce the number of workers."
                            )
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, FileNotFoundError):
                # Fallback to PyTorch memory check if nvidia-smi is not available
                torch.cuda.empty_cache()  # Clear any cached memory
                total_memory = torch.cuda.get_device_properties(0).total_memory
                allocated_memory = torch.cuda.memory_allocated(0)
                reserved_memory = torch.cuda.memory_reserved(0)
                free_memory = total_memory - allocated_memory - reserved_memory
                free_memory_gb = free_memory / (1024**3)
                
                # More conservative check
                if free_memory_gb < required_memory_gb + 2.0:  # Add 2GB buffer
                    raise RuntimeError(
                        f"Insufficient GPU memory. Required: {required_memory_gb + 2.0:.1f}GB, "
                        f"Available: {free_memory_gb:.1f}GB. "
                        f"Total: {total_memory / (1024**3):.1f}GB, "
                        f"Allocated: {allocated_memory / (1024**3):.1f}GB, "
                        f"Reserved: {reserved_memory / (1024**3):.1f}GB. "
                        f"Please wait for other workers to finish or reduce the number of workers."
                    )
            
            # Load model
            try:
                from chandra.model import InferenceManager
                from chandra.output import parse_markdown
                
                import sys
                
                # Suppress output during model loading to avoid broken pipe errors
                # This is especially important in RQ worker processes
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                
                try:
                    # Redirect stdout/stderr to devnull during model loading
                    with open(os.devnull, 'w') as devnull:
                        sys.stdout = devnull
                        sys.stderr = devnull
                        
                        # Use InferenceManager as per Hugging Face documentation
                        # https://huggingface.co/datalab-to/chandra
                        # This handles model loading and generation internally
                        cls._inference_manager = InferenceManager(method="hf")
                        cls._parse_markdown = parse_markdown
                finally:
                    # Restore stdout/stderr
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                
                cls._model_loaded = True
                
            except ImportError as e:
                # Release lock on error
                if lock_file:
                    try:
                        if HAS_FCNTL:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                        else:
                            lock_file.close()
                            if os.path.exists(lock_file_path):
                                os.remove(lock_file_path)
                    except:
                        pass
                raise ImportError(
                    f"Chandra dependencies not installed. "
                    f"Install with: pip install chandra-ocr transformers torch. "
                    f"Error: {str(e)}"
                )
            except Exception as e:
                # Release lock on error
                if lock_file:
                    try:
                        if HAS_FCNTL:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                        else:
                            lock_file.close()
                            if os.path.exists(lock_file_path):
                                os.remove(lock_file_path)
                    except:
                        pass
                raise RuntimeError(
                    f"Failed to load Chandra model: {str(e)}"
                )
        except Exception as e:
            # Release lock on error (from lock acquisition or memory check)
            if lock_file:
                try:
                    if HAS_FCNTL:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    else:
                        lock_file.close()
                        if os.path.exists(lock_file_path):
                            os.remove(lock_file_path)
                except:
                    pass
            raise
        finally:
            # Release lock
            if lock_file:
                try:
                    if HAS_FCNTL:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    else:
                        lock_file.close()
                        if os.path.exists(lock_file_path):
                            os.remove(lock_file_path)
                except:
                    pass
                try:
                    lock_file.close()
                except:
                    pass
    
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
        import sys
        import os
        
        # Load image (page-level: always page 0)
        image = self._load_image(document.file_path, page_number=0)
        
        # Prepare batch
        batch = [BatchInputItem(image=image, prompt_type="ocr_layout")]
        
        # Suppress output during inference to avoid broken pipe errors
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Redirect stdout/stderr during inference
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                sys.stderr = devnull
                
                # Generate result using InferenceManager
                # This follows the Hugging Face documentation example
                result = ChandraParser._inference_manager.generate(batch)[0]
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
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
