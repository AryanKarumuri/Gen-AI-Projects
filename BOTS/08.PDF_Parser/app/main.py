import os
import logging
import asyncio
import time
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.routes import router as document_parser_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="VLM File Processor API",
    description="API to process PDF and image files.",
    version="1.0.0"
)

# Include API routes
app.include_router(document_parser_router)

# Get allowed origins from environment variable, default to empty list for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event() -> None:
    global cleanup_old_files
    cleanup_old_files = asyncio.create_task(cleanup_files())

@app.on_event("shutdown")
async def shutdown_event() -> None:
    if cleanup_old_files:
        cleanup_old_files.cancel()
        try:
            await cleanup_old_files
        except asyncio.CancelledError:
            pass

async def cleanup_files() -> None:
    """Delete files older than 1 hour in the output directory."""
    OUTPUT_DIR = "app/outputs"
    TEN_MINUTES = 0.1 * 60 * 60  # seconds
    
    while True:
        try:
            if os.path.exists(OUTPUT_DIR):
                current_time = time.time()
                for filename in os.listdir(OUTPUT_DIR):
                    try:
                        file_path = os.path.join(OUTPUT_DIR, filename)
                        if os.path.isfile(file_path):
                            file_age = current_time - os.path.getmtime(file_path)
                            if file_age > TEN_MINUTES:
                                os.remove(file_path)
                                logger.info(f"Deleted old file: {filename}")
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Could not process file {filename}: {e}")
                        continue
            
            # Wait for 1 hour before next cleanup
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour before retrying
