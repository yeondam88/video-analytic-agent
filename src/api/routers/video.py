from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List
import logging

from ..services.video_service import VideoService
from ..db.models.video import Video
from ..db.session import get_db
from src.pipeline.types import VideoStatus

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