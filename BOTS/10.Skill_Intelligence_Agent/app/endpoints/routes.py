from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.engine import run_engine

router = APIRouter(prefix="/api", tags=["skill-engine"])


class SkillQuery(BaseModel):
    query: str = Field(..., example="Python data science libraries")
    num_results: int = Field(
        10,
        ge=1,
        le=50,
        description="How many search results to fetch from SearXNG before analysis",
    )


@router.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}


@router.post("/extract-skills", summary="Extract skills from query")
def extract_skills(payload: SkillQuery):
    try:
        result = run_engine(payload.query, payload.num_results)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
