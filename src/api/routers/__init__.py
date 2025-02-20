"""API router module that combines all route handlers."""
from fastapi import APIRouter

from .base import router as base_router
from .video import router as video_router
from .search import router as search_router
from .queue import router as queue_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(base_router, tags=["base"])
api_router.include_router(video_router, prefix="/videos", tags=["videos"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(queue_router, prefix="/queue", tags=["queue"])

__all__ = ["api_router"] 