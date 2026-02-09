"""Configuration settings."""
from typing import Dict, Any, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Parser Settings
    DEFAULT_PARSER: str = "unstructured"
    DEFAULT_PARSE_MODE: str = "basic"  # Default parse mode: 'basic' or 'enhance'
    
    # Parser Configurations
    PARSER_CONFIGS: Dict[str, Dict[str, Any]] = {
        "docling": {
            # Docling configuration
            "enable_remote_services": False,  # Set to True if using remote vision models
            # OCR options (important for image files)
            "do_ocr": True,  # Force OCR for image files
            "generate_picture_images": True,
            "images_scale": 2,
            # Table extraction
            "do_table_structure": True,  # Enable table structure recognition
            "table_structure_options": {
                "do_cell_matching": True,  # Map structure back to PDF cells (default)
            },
            # Enrichments
            "do_picture_description": True,  # Use vision model for image description
            "do_picture_classification": False,
            "do_code_enrichment": False,
            "do_formula_enrichment": False,
        },
        "chandra": {
            # Chandra configuration
            "model_path": "datalab-to/chandra",
            "use_gpu": True,
        },
    }
    
    # Storage Settings
    UPLOAD_DIR: str = "./uploads"
    
    # Redis Settings (for RQ)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Parser API Settings (Remote) — docling/chandra requests go here
    # Override in .env: PARSER_API_BASE_URL, PARSER_API_ENABLED (False = use local parsers)
    PARSER_API_ENABLED: bool = True  # Use remote parser API
    PARSER_API_BASE_URL: str = "http://194.68.245.19:22159"  # Must be reachable; Connection refused = server down or unreachable
    PARSER_API_TIMEOUT: int = 360  # Timeout in seconds (6 minutes)
    PARSER_API_RETRY_COUNT: int = 3  # Number of retry attempts
    PARSER_API_RETRY_DELAY: float = 1.0  # Delay between retries in seconds
    
    # Peter-parser API Settings (Chunking) — POST /parse, GET /status, GET /result
    PETER_PARSER_BASE_URL: str = "http://localhost:8001"
    PETER_PARSER_TIMEOUT: int = 360  # Timeout in seconds (6 minutes)
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars (e.g. OPENAI_API_KEY) not defined in Settings


# Create settings instance
settings = Settings()
