"""
Configuration management for RAG Chatbot
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    
    # Server Configuration
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    port: int = int(os.getenv("PORT", 8000))
    
    # ChromaDB Configuration
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
    
    # Application Settings
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 50))
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", 5))
    
    # Upload directory
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_directory, exist_ok=True)
