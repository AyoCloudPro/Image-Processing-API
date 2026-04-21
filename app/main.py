import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import images
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger =  logging.getLogger(__name__)

app = FastAPI(
    title="Image Processing API",
    description=(
        "A production-ready image processing API deployed on GCP cloud Run."
        "Supports resizing, compression, and format conversion via signed GCS URLs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router, prefix="/images", tags=["images"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint used by Cloud Run."""
    return {"status": "healthy", "version": settings.app_version}