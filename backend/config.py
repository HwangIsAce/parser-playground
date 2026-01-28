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
            # Note: do_picture_description requires vision model (remote or local)
            # Disable if enable_remote_services is False and no local vision model available
            "do_picture_description": False,  # Disabled - requires vision model
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
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()
