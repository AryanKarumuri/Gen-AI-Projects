from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.routes import router as skill_engine_router

app = FastAPI(
    title="Skill Engine Agent API",
    description="API for the Skill Engine Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skill_engine_router)
