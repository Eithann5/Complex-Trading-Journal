from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings

app = FastAPI(title="Complex Trading Journal Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.data_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.data_dir), name="static")

app.include_router(api_router, prefix=settings.api_prefix)
