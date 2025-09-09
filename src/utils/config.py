"""
Configuration management for the AI Research Assistant.

This module handles loading and managing configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and defaults.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Check for required environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    
    config = {
        # API Configuration
        "groq_api_key": groq_api_key,
        "groq_model": os.getenv("GROQ_MODEL", "llama3-8b-8192"),
        
        # Server Configuration
        "server_name": os.getenv("SERVER_NAME", "0.0.0.0"),
        "server_port": int(os.getenv("SERVER_PORT", "7860")),
        "share": os.getenv("SHARE", "false").lower() == "true",
        "debug": os.getenv("DEBUG", "true").lower() == "true",
        
        # Vector Database Configuration
        "vector_db_path": os.getenv("VECTOR_DB_PATH", "./data/vector_db"),
        "collection_name": os.getenv("COLLECTION_NAME", "documents"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        
        # Document Processing Configuration
        "chunk_size": int(os.getenv("CHUNK_SIZE", "500")),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "50")),
        "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", "50")),
        
        # AI Configuration
        "max_tokens": int(os.getenv("MAX_TOKENS", "1024")),
        "temperature": float(os.getenv("TEMPERATURE", "0.1")),
        "top_k_results": int(os.getenv("TOP_K_RESULTS", "5")),
        
        # Paths
        "data_dir": Path(os.getenv("DATA_DIR", "./data")),
        "upload_dir": Path(os.getenv("UPLOAD_DIR", "./data/uploads")),
    }
    
    # Create necessary directories
    config["data_dir"].mkdir(exist_ok=True)
    config["upload_dir"].mkdir(exist_ok=True)
    
    return config


def get_supported_file_types() -> Dict[str, str]:
    """
    Get supported file types and their descriptions.
    
    Returns:
        Dict[str, str]: Dictionary mapping file extensions to descriptions
    """
    return {
        ".pdf": "PDF Documents",
        ".docx": "Microsoft Word Documents",
        ".txt": "Plain Text Files"
    }


def validate_file_size(file_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate file size is within limits.
    
    Args:
        file_path (str): Path to the file
        max_size_mb (int): Maximum file size in MB
        
    Returns:
        bool: True if file size is valid
    """
    try:
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    except OSError:
        return False


def validate_file_type(filename: str) -> bool:
    """
    Validate if file type is supported.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file type is supported
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in get_supported_file_types()


class ConfigManager:
    """Configuration manager class for the application."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._config = load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key (str): Configuration key
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)
    
    def update(self, key: str, value: Any) -> None:
        """
        Update configuration value.
        
        Args:
            key (str): Configuration key
            value (Any): New value
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dict[str, Any]: All configuration values
        """
        return self._config.copy()
    
    def reload(self) -> None:
        """Reload configuration from environment."""
        self._config = load_config()