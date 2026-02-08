import os
import tempfile
import logging
import base64
from io import BytesIO
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from app.services.image_generation import image_generation_fun
from app.models.schemas import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    HealthResponse
)
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["image-generation"],
)


def cleanup_temp_file(file_path: str) -> None:
    """Clean up temporary file in the background."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")


@router.get("/")
async def root() -> dict:
    """Root endpoint with welcome message."""
    return {"message": "Welcome to the Image Generation API!"}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.version)


@router.post("/generate-image")
async def generate_image(
    request: ImageGenerationRequest,
    x_huggingface_token: str = Header(..., alias="X-HuggingFace-Token"),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> FileResponse:
    """
    Generate an image and return it as a file.
    
    Args:
        request: Image generation request with prompt and parameters
        x_huggingface_token: Hugging Face API token (from header)
        background_tasks: FastAPI background tasks for cleanup
    
    Returns:
        FileResponse: Generated image file
    """
    try:
        logger.info("Received image generation request")

        # Generate image
        image = await image_generation_fun(
            prompt=request.text,
            huggingface_token=x_huggingface_token,
            width=request.width,
            height=request.height,
            model=request.model
        )

        # Save image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image.save(tmp_file.name)
            tmp_file_path = tmp_file.name
            logger.info(f"Image saved to temporary file: {tmp_file_path}")
        
        # Schedule cleanup in background (after response is sent)
        background_tasks.add_task(cleanup_temp_file, tmp_file_path)
        
        return FileResponse(
            tmp_file_path,
            media_type="image/png",
            filename="generated_image.png"
        )
    
    except ValueError as e:
        logger.error(f"Validation error in generate_image endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in generate_image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate-image-json", response_model=ImageGenerationResponse)
async def generate_image_json(
    request: ImageGenerationRequest,
    x_huggingface_token: str = Header(..., alias="X-HuggingFace-Token")
) -> ImageGenerationResponse:
    """
    Generate an image and return it as base64-encoded JSON.
    
    Args:
        request: Image generation request with prompt and parameters
        x_huggingface_token: Hugging Face API token (from header)
    
    Returns:
        ImageGenerationResponse: Base64 encoded image
    """
    try:
        logger.info("Received image generation request (JSON)")

        # Generate image
        image = await image_generation_fun(
            prompt=request.text,
            huggingface_token=x_huggingface_token,
            width=request.width,
            height=request.height,
            model=request.model
        )

        # Convert image to base64 string
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return ImageGenerationResponse(image=img_str, format="PNG")
    
    except ValueError as e:
        logger.error(f"Validation error in generate_image_json endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in generate_image_json endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

