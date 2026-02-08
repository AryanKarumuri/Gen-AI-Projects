from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def image_generation_fun(
    prompt: str,
    huggingface_token: str,
    width: int = 512,
    height: int = 512,
    model: str = "black-forest-labs/FLUX.1-schnell"
):
    try:
        logger.info("Starting image generation process")

        # Validate token
        if not huggingface_token:
            logger.error("Hugging Face token is missing")
            raise ValueError("Hugging Face token is required")

        # Validate prompt
        if not prompt or not prompt.strip():
            logger.error("Prompt is empty")
            raise ValueError("Prompt cannot be empty")

        # Validate dimensions
        if width <= 0 or height <= 0:
            logger.error(f"Invalid dimensions: {width}x{height}")
            raise ValueError("Width and height must be positive integers")

        # Create client
        client = InferenceClient(token=huggingface_token)
        logger.info("Successfully created InferenceClient")

        # Generate image
        logger.info(f"Generating image with model: {model}, dimensions: {width}x{height}")
        image = client.text_to_image(
            prompt=prompt,
            model=model,
            width=width,
            height=height
        )
        logger.info("Image generation successful")
        
        return image

    except HfHubHTTPError as e:
        logger.error(f"Hugging Face API error: {str(e)}")
        if e.response.status_code == 401:
            raise ValueError("Invalid Hugging Face token") from e
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded. Please try again later.") from e
        else:
            raise ValueError(f"Hugging Face API error: {str(e)}") from e
    
    except RepositoryNotFoundError as e:
        logger.error(f"Model not found: {model}")
        raise ValueError(f"Model '{model}' not found on Hugging Face") from e
    
    except ValueError as e:
        # Re-raise ValueError as-is
        raise e
    
    except Exception as e:
        logger.error(f"Unexpected error during image generation: {str(e)}")
        raise Exception(f"Failed to generate image: {str(e)}") from e