from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from loguru import logger

from ..services.video_service import VideoService
from ..db.models.video import Video
from ..db.session import get_db
from src.pipeline.types import VideoStatus
from src.api.dependencies.database import get_db
from src.api.schemas.video import VideoCreate, VideoResponse, VideoUpdate
from src.api.schemas.queue import QueueItemCreate, QueueItemResponse
from src.api.services.queue_service import QueueService
from src.db.models.queue import QueueStatus

router = APIRouter()
logger = logging.getLogger(__name__)

class VideoProcessRequest(BaseModel):
    url: HttpUrl

class VideoResponse(BaseModel):
    id: str
    url: str
    title: str | None = None
    status: str
    error: str | None = None
    progress: float = 0.0
    steps_completed: List[str] = []

@router.post("/process")
async def process_video(
    request: VideoProcessRequest,
    background_tasks: BackgroundTasks,
) -> VideoResponse:
    try:
        # Initialize video service
        db = next(get_db())
        video_service = VideoService(db)
        
        # Create video record with PENDING status
        video = video_service.create_video(str(request.url), status=VideoStatus.PENDING)
        
        # Start background processing
        background_tasks.add_task(
            video_service.process_video,
            video.id
        )
        
        return VideoResponse(
            id=str(video.id),
            url=str(request.url),
            status=video.status.value,
            progress=video.progress,
            steps_completed=video.steps_completed or []
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )

@router.get("/{video_id}")
async def get_video(video_id: str) -> VideoResponse:
    try:
        db = next(get_db())
        video_service = VideoService(db)
        video = video_service.get_video(int(video_id))
        
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video with id {video_id} not found"
            )
            
        return VideoResponse(
            id=str(video.id),
            url=video.url,
            title=video.title,
            status=video.status.value,
            error=video.error,
            progress=video.progress,
            steps_completed=video.steps_completed or []
        )
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video ID format: {video_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video: {str(e)}"
        )

@router.post("/queue", response_model=List[QueueItemResponse])
def add_to_queue(
    urls: List[str],
    priority: Optional[int] = Query(0, ge=0, le=10),
    db: Session = Depends(get_db)
) -> List[QueueItemResponse]:
    """Add multiple URLs to the processing queue."""
    try:
        queue_service = QueueService(db)
        queue_items = queue_service.add_to_queue(urls=urls, priority=priority)
        return [QueueItemResponse.from_orm(item) for item in queue_items]
    except Exception as e:
        logger.error(f"Failed to add URLs to queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue", response_model=List[QueueItemResponse])
def get_queue_items(
    status: Optional[QueueStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_completed: bool = Query(False),
    is_bulk: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[QueueItemResponse]:
    """Get queue items with optional filtering."""
    try:
        queue_service = QueueService(db)
        items = queue_service.get_items(
            status=status,
            skip=skip,
            limit=limit,
            include_completed=include_completed,
            is_bulk=is_bulk
        )
        return [QueueItemResponse.from_orm(item) for item in items]
    except Exception as e:
        logger.error(f"Failed to get queue items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/{item_id}", response_model=QueueItemResponse)
def get_queue_item(
    item_id: str,
    db: Session = Depends(get_db)
) -> QueueItemResponse:
    """Get a specific queue item by ID."""
    try:
        queue_service = QueueService(db)
        item = queue_service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Queue item not found")
        return QueueItemResponse.from_orm(item)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get queue item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/retry-failed")
def retry_failed_items(
    db: Session = Depends(get_db)
) -> dict:
    """Retry all failed items in the queue."""
    try:
        queue_service = QueueService(db)
        count = queue_service.retry_failed()
        return {"retried_count": count}
    except Exception as e:
        logger.error(f"Failed to retry failed items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/clear-completed")
def clear_completed_items(
    days_old: int = Query(7, ge=1),
    db: Session = Depends(get_db)
) -> dict:
    """Clear completed items older than specified days."""
    try:
        queue_service = QueueService(db)
        count = queue_service.clear_completed(days_old=days_old)
        return {"cleared_count": count}
    except Exception as e:
        logger.error(f"Failed to clear completed items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/status")
def get_queue_status(
    db: Session = Depends(get_db)
) -> dict:
    """Get the current status of the queue."""
    try:
        queue_service = QueueService(db)
        return queue_service.get_queue_status()
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 