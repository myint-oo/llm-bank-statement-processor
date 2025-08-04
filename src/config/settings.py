"""
Configuration settings for the API
This file manages all environment variables and app settings
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings class
    This centralizes all configuration in one place
    """
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "7079"))
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-this-secret-key")
    API_KEY: str = os.getenv("API_KEY", "default-api-key")
    
    # CORS (Cross-Origin Resource Sharing) - allows Laravel to call this API
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost").split(",")
    
    # Model Configuration
    BASE_MODEL: str = os.getenv("BASE_MODEL", "openchat/openchat_3.5")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf"]
    
    # API Metadata
    API_TITLE: str = "Enston AI"
    API_DESCRIPTION: str = "Enston AI API"
    API_VERSION: str = "1.0.0"

settings = Settings()
