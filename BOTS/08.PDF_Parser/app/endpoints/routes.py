import os
import logging
from typing import Optional
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.services.parser import parse_file as parse_file_service

SUPPORTED_FORMATS = ['pdf', 'png', 'jpg', 'jpeg']
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3-vl:235b-instruct-cloud")
OUTPUT_DIR = "app/outputs"

if os.path.exists(OUTPUT_DIR) is False:
    os.makedirs(OUTPUT_DIR)

router = APIRouter(prefix="/api", tags=["pdf and image parser"])

@router.get("/")
async def root() -> dict:
    return {"message": "Welcome to VLM File Processor API"}

@router.get("/formats")
async def get_formats() -> dict:
    return {"formats": SUPPORTED_FORMATS}

@router.post("/parse-file")
async def parse_file_handler(
    file: UploadFile = File(...),
    model: Optional[str] = Form(DEFAULT_MODEL),
    output_dir: str = Form(OUTPUT_DIR)
) -> FileResponse:
    # Validate file size (e.g., max 50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum limit of 50MB.")
    
    # Validate file format
    ext = file.filename.split('.')[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Supported formats: {SUPPORTED_FORMATS}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
        temp_file_path = temp_file.name

    try:
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

            markdown_conversion = parse_file_service(temp_file_path, model=model, original_filename=file.filename)

            output_filename = os.path.splitext(file.filename)[0] + ".md"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as out_f:
                for page_num, content in enumerate(markdown_conversion, start=1):
                    if len(markdown_conversion) > 1:  # Multiple pages (PDF)
                        out_f.write(f"<!-- Page {page_num} -->\n")
                    out_f.write(content)
                    out_f.write("\n\n")
        return JSONResponse(content={"status": "success", "output_path": output_path, "filename": output_filename}, media_type='application/json')
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    
@router.get("/output")
async def list_output_files() -> dict:
    """List all generated markdown files."""
    if not os.path.exists(OUTPUT_DIR):
        return {"files": []}
    
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    return {"files": files, "count": len(files)}


@router.get("/output/{filename}")
async def get_output_file(filename: str) -> FileResponse:
    """Get the generated markdown file."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename)


@router.delete("/output/{filename}")
async def delete_output_file(filename: str) -> dict:
    """Delete a generated markdown file."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"success": True, "message": f"Deleted {filename}"}
    
