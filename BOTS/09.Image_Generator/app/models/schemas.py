from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt for image generation"
    )
    width: Optional[int] = Field(
        default=512,
        ge=64,
        le=2048,
        description="Image width in pixels"
    )
    height: Optional[int] = Field(
        default=512,
        ge=64,
        le=2048,
        description="Image height in pixels"
    )
    model: Optional[str] = Field(
        default="black-forest-labs/FLUX.1-schnell",
        description="Hugging Face model identifier"
    )
    
    @validator('model')
    def validate_model(cls, v):
        """Validate that the model is in the allowed list."""
        from app.config import settings
        if v not in settings.allowed_models:
            raise ValueError(
                f"Model '{v}' is not allowed. Allowed models: {', '.join(settings.allowed_models)}"
            )
        return v


class ImageGenerationResponse(BaseModel):
    """Response model for image generation (JSON format)."""
    
    image: str = Field(..., description="Base64 encoded image")
    format: str = Field(default="PNG", description="Image format")
    

class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")