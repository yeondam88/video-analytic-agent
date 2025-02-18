from typing import Generator
from fastapi import Depends

from src.api.services.video_service import VideoService
from src.api.services.summary_service import SummaryService
from src.api.services.embedding_service import EmbeddingService
from src.api.services.storage_cleanup import StorageCleanupService
from src.db.database import db

# Update imports to use new model locations
from src.db.models.video import Video
from src.db.models.segment import Segment
from src.db.models.summary import Summary

def get_video_service() -> Generator[VideoService, None, None]:
    """Dependency for video service."""
    service = VideoService(db)
    try:
        yield service
    finally:
        pass  # Add cleanup if needed

def get_summary_service() -> Generator[SummaryService, None, None]:
    """Dependency for summary service."""
    service = SummaryService(db)
    try:
        yield service
    finally:
        pass

def get_embedding_service() -> Generator[EmbeddingService, None, None]:
    """Dependency for embedding service."""
    service = EmbeddingService(db)
    try:
        yield service
    finally:
        pass

def get_storage_service() -> Generator[StorageCleanupService, None, None]:
    """Dependency for storage cleanup service."""
    service = StorageCleanupService()
    try:
        yield service
    finally:
        service.cleanup_old_files()  # Clean up on context exit

# Common dependencies
CommonDeps = {
    "video_service": Depends(get_video_service),
    "summary_service": Depends(get_summary_service),
    "embedding_service": Depends(get_embedding_service),
    "storage_service": Depends(get_storage_service)
} 