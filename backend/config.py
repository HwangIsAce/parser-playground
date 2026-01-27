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
    
    # Parser Configurations
    PARSER_CONFIGS: Dict[str, Dict[str, Any]] = {}
    
    # Storage Settings
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()
