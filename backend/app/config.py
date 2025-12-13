"""
Configuration settings for the AI Clinical Documentation Copilot backend.
Uses Pydantic Settings for environment variable management.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys - REQUIRED: Set via environment variable
    groq_api_key: str  # No default - must be set in environment
    
    # Application Settings
    app_name: str = "AI Clinical Documentation Copilot"
    debug: bool = False  # Default to False for production
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    chroma_dir: Path = base_dir / "chroma_db"
    db_path: Path = base_dir / "sessions.db"
    
    # Whisper Settings - Can be overridden via WHISPER_MODEL env var
    whisper_model: str = "small"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # cpu or cuda
    whisper_compute_type: str = "int8"  # float16, int8
    
    # Groq Settings
    groq_model: str = "llama-3.3-70b-versatile"
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.3
    
    # RAG Settings
    embedding_model: str = "all-mpnet-base-v2"
    rag_top_k: int = 3
    
    # File Upload Settings
    max_audio_size_mb: int = 50
    max_notes_size_mb: int = 10
    allowed_audio_extensions: list = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    allowed_notes_extensions: list = [".txt", ".pdf", ".doc", ".docx"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    
    # Ensure directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    
    return settings


# Global settings instance
settings = get_settings()
