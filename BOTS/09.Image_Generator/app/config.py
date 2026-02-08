from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    # API Configuration
    title: str = "Image Generation API"
    description: str = "API for generating images"
    version: str = "1.0.0"
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]  # Default to all origins, override in production
    
    # Hugging Face Configuration
    huggingface_token: str = ""
    
    # Image Generation Configuration
    default_model: str = "black-forest-labs/FLUX.1-schnell"
    default_width: int = 512
    default_height: int = 512
    max_width: int = 2048
    max_height: int = 2048
    min_width: int = 64
    min_height: int = 64
    
    # Allowed Models (whitelist)
    allowed_models: List[str] = [
        "black-forest-labs/FLUX.1-schnell",
        "black-forest-labs/FLUX.1-dev",
        "stabilityai/stable-diffusion-3-medium-diffusers",
        "stabilityai/stable-diffusion-xl-base-1.0",
    ]


settings = Settings()