from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Path
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session
from loguru import logger
from sqlalchemy.sql import text
import re
import os
import httpx
from datetime import datetime

from src.db.models.video import Video
from src.pipeline.types import VideoStatus, VideoSource
from src.api.database import get_db, db
from src.api.schemas.video import VideoCreate, VideoResponse, VideoUpdate, VideoSimilarityResponse
from src.api.schemas.queue import QueueItemCreate, QueueItemResponse
from src.api.services.queue_service import QueueService
from src.api.services.video_service import VideoService
from src.db.models.queue import QueueStatus
from src.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class VideoProcessRequest(BaseModel):
    url: HttpUrl

class VideoInsights(BaseModel):
    analysis: Dict[str, Any] = {}
    top_keywords: List[str] = []
    speaker_statistics: Dict[str, Any] = {}
    timeline_highlights: List[Any] = []

class VideoMetadata(BaseModel):
    summary: Optional[str] = None
    insights: VideoInsights = VideoInsights()
    key_points: List[str] = []

class VideoResponse(BaseModel):
    id: str
    url: str
    title: str | None = None
    description: str | None = None
    status: str
    error: str | None = None
    progress: float = 0.0
    steps_completed: List[str] = []
    duration: float | None = None
    source: VideoSource | None = None
    thumbnail_url: str | None = None
    extra_data: Dict[str, Any] | None = None
    metadata: VideoMetadata | None = None
    created_at: str
    updated_at: str | None = None
    deleted_at: str | None = None
    segments_count: int = 0
    has_summary: bool = False
    processing_progress: float = 0.0

# Helper Functions
def get_thumbnail_url(video_url: str) -> Optional[str]:
    """Get thumbnail URL for a video based on its source."""
    try:
        # YouTube URL patterns
        youtube_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        ]
        
        # Loom URL pattern
        loom_pattern = r'(?:https?:\/\/)?(?:www\.)?loom\.com\/share\/([a-zA-Z0-9]+)'
        
        # Check for YouTube
        for pattern in youtube_patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                # YouTube thumbnail resolutions in order of preference
                thumbnail_urls = [
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # HD (1920x1080)
                    f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",      # SD (640x480)
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",      # HQ (480x360)
                    f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",      # MQ (320x180)
                    f"https://img.youtube.com/vi/{video_id}/default.jpg",        # Default (120x90)
                ]
                
                # Check if thumbnail exists by making a HEAD request
                for url in thumbnail_urls:
                    try:
                        response = httpx.head(url)
                        if response.status_code == 200:
                            logger.info(f"Using YouTube thumbnail: {url}")
                            return url
                    except Exception as e:
                        logger.debug(f"Failed to check thumbnail {url}: {e}")
                        continue
                
                # If all checks fail, return the default thumbnail
                return thumbnail_urls[-1]
        
        # Check for Loom
        loom_match = re.search(loom_pattern, video_url)
        if loom_match:
            video_id = loom_match.group(1)
            return f"https://cdn.loom.com/sessions/thumbnails/{video_id}-with-play.gif"
        
        # Return None if no match found
        logger.warning(f"Could not generate thumbnail URL for video: {video_url}")
        return None
        
    except Exception as e:
        logger.error(f"Error generating thumbnail URL for {video_url}: {str(e)}")
        return None

# Video Routes
@router.get("/", response_model=List[VideoResponse])
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[VideoResponse]:
    """Get all videos with pagination."""
    try:
        video_service = VideoService(db)
        videos = video_service.list_videos(skip=skip, limit=limit)
        
        responses = []
        for video in videos:
            # Convert metadata to VideoMetadata model if it exists
            metadata = None
            if video.get("metadata"):
                try:
                    metadata_dict = video["metadata"]
                    metadata = VideoMetadata(
                        summary=metadata_dict.get('summary'),
                        key_points=metadata_dict.get('key_points', []),
                        insights=VideoInsights(
                            analysis=metadata_dict.get('insights', {}).get('analysis', {}),
                            top_keywords=metadata_dict.get('insights', {}).get('top_keywords', []),
                            speaker_statistics=metadata_dict.get('insights', {}).get('speaker_statistics', {}),
                            timeline_highlights=metadata_dict.get('insights', {}).get('timeline_highlights', [])
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse metadata for video {video['id']}: {e}")
                    metadata = None
                    
            # Create response with all available fields
            response = VideoResponse(
                id=str(video["id"]),
                url=video["url"],
                title=video.get("title"),
                description=video.get("description"),
                status=video["status"],
                error=video.get("error"),
                progress=video.get("progress", 0.0),
                steps_completed=video.get("steps_completed", []),
                duration=video.get("duration"),
                source=video.get("source"),
                thumbnail_url=video.get("thumbnail_url"),
                extra_data=video.get("extra_data", {}),
                metadata=metadata,
                created_at=video.get("created_at"),
                updated_at=video.get("updated_at"),
                deleted_at=video.get("deleted_at"),
                segments_count=video.get("segments_count", 0),
                has_summary=bool(video.get("summary")),
                processing_progress=video.get("progress", 0.0)
            )
            responses.append(response)
            
        return responses
        
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list videos: {str(e)}"
        )

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
            title=video.title,
            description=video.description,
            status=video.status.value,
            progress=video.progress,
            steps_completed=video.steps_completed or [],
            duration=video.duration,
            source=video.source,
            thumbnail_url=video.thumbnail_url,
            extra_data=video.extra_data,
            metadata=video.metadata,
            created_at=video.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )

@router.get("/{video_id}")
async def get_video(video_id: str) -> VideoResponse:
    """Get a specific video by ID."""
    try:
        logger.info(f"Fetching video with ID: {video_id}")
        db_session = next(get_db())
        video_service = VideoService(db_session)
        
        # Get video data using service
        video = video_service.get_video(video_id)
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Video with id {video_id} not found"
            )
            
        logger.info(f"Raw video data: {video}")
        
        # Convert metadata to VideoMetadata model if it exists
        metadata = None
        if video.get("metadata"):
            try:
                logger.info(f"Processing metadata for video {video_id}")
                metadata_dict = video["metadata"]
                
                # Create VideoMetadata instance
                metadata = VideoMetadata(
                    summary=metadata_dict.get('summary'),
                    key_points=metadata_dict.get('key_points', []),
                    insights=VideoInsights(
                        analysis=metadata_dict.get('insights', {}).get('analysis', {}),
                        top_keywords=metadata_dict.get('insights', {}).get('top_keywords', []),
                        speaker_statistics=metadata_dict.get('insights', {}).get('speaker_statistics', {}),
                        timeline_highlights=metadata_dict.get('insights', {}).get('timeline_highlights', [])
                    )
                )
                logger.info(f"Successfully processed metadata for video {video_id}")
            except Exception as e:
                logger.warning(f"Failed to parse metadata for video {video_id}: {e}")
                metadata = None
        
        # Create response with all available fields
        response = VideoResponse(
            id=str(video["id"]),
            url=video["url"],
            title=video.get("title"),
            description=video.get("description"),
            status=video["status"],
            error=video.get("error"),
            progress=video.get("progress", 0.0),
            steps_completed=video.get("steps_completed", []),
            duration=video.get("duration"),
            source=video.get("source"),
            thumbnail_url=video.get("thumbnail_url"),
            extra_data=video.get("extra_data", {}),
            metadata=metadata,
            created_at=video.get("created_at"),
            updated_at=video.get("updated_at"),
            deleted_at=video.get("deleted_at"),
            segments_count=video.get("segments_count", 0),
            has_summary=bool(video.get("summary")),
            processing_progress=video.get("progress", 0.0)
        )
        
        logger.info(f"Successfully retrieved video {video_id}")
        logger.debug(f"Response data: {response.dict()}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video {video_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video: {str(e)}"
        )

@router.put("/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    video: VideoUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific video."""
    try:
        service = VideoService(db)
        updated_video = service.update_video(video_id, **video.model_dump(exclude_unset=True))
        if not updated_video:
            raise HTTPException(
                status_code=404,
                detail=f"Video with ID {video_id} not found"
            )
        return updated_video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update video {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update video: {str(e)}"
        )

@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Delete a video and its associated files."""
    try:
        # Get video from database using direct Supabase client
        result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Video not found")
            
        video = result.data[0]
        source_id = video.get("source_id")
        
        if not source_id:
            logger.warning(f"No source_id found for video {video_id}")
            
        # Construct file paths
        video_path = settings.paths.VIDEO_DIR / f"{source_id}.mp4" if source_id else None
        audio_path = settings.paths.AUDIO_DIR / f"{source_id}.wav" if source_id else None
        
        # Delete files if they exist
        try:
            if video_path and video_path.exists():
                logger.info(f"Deleting video file: {video_path}")
                os.remove(video_path)
                
            if audio_path and audio_path.exists():
                logger.info(f"Deleting audio file: {audio_path}")
                os.remove(audio_path)
                
        except Exception as file_error:
            logger.error(f"Error deleting files for video {video_id}: {str(file_error)}")
            # Continue with database deletion even if file deletion fails
            
        # Delete associated data
        try:
            # Delete segments
            db.supabase.table("segments").delete().eq("video_id", video_id).execute()
            logger.info(f"Deleted segments for video {video_id}")
            
            # Delete transcriptions
            db.supabase.table("transcriptions").delete().eq("video_id", video_id).execute()
            logger.info(f"Deleted transcriptions for video {video_id}")
            
            # Delete video record
            db.supabase.table("videos").delete().eq("id", video_id).execute()
            logger.info(f"Deleted video record {video_id}")
            
            return {"message": "Video and associated data deleted successfully"}
            
        except Exception as db_error:
            logger.error(f"Database error while deleting video {video_id}: {str(db_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete video data: {str(db_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {str(e)}")
        logger.exception(e)  # Log full traceback
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )

@router.get("/{video_id}/similar", response_model=List[VideoSimilarityResponse])
async def get_similar_videos(
    vid: int = Path(..., alias="video_id"),
    limit: int = Query(default=5, ge=1, le=20), 
    threshold: float = Query(default=0.7, ge=0.0, le=1.0),
) -> List[VideoSimilarityResponse]:
    """Get similar videos based on content similarity."""
    try:
        # Get similar videos using the database function
        similar_result = db.supabase.rpc(
            'get_similar_videos',
            {
                'exclude_video_id': str(vid),
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()

        if not similar_result.data:
            logger.info(f"No similar videos found for video {vid} with threshold {threshold}")
            return []

        # Transform results
        responses = []
        for video in similar_result.data:
            similarity_score = round(float(video["similarity"]) * 100, 2)
            source_id = video.get('source_id')
            thumbnail_url = f"https://img.youtube.com/vi/{source_id}/mqdefault.jpg" if source_id else None
            
            logger.info(
                f"Found similar video {video['id']} with {similarity_score}% similarity"
            )
            
            responses.append(
                VideoSimilarityResponse(
                    id=int(video["id"]),  # Convert ID to integer
                    title=video.get("title") or "Untitled Video", 
                    url=video["url"],
                    thumbnail_url=thumbnail_url,
                    similarity_score=similarity_score,
                    segment_count=video.get("segment_count", 0),
                    avg_confidence=round(float(video.get("avg_confidence", 0)) * 100, 2)
                )
            )

        return responses

    except Exception as e:
        logger.error(f"Error getting similar videos for video {vid}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting similar videos: {str(e)}"
        )

@router.get("/{video_id}/segments")
async def get_video_segments(
    video_id: str,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all segments for a specific video."""
    try:
        # Get the video service
        video_service = VideoService(db)
        
        # Check if video exists
        video = video_service.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video with id {video_id} not found"
            )
            
        # Get segments using service
        segments = video_service.get_video_segments(video_id)
        
        # Format segments for response
        formatted_segments = []
        for segment in segments:
            # Convert start_time and end_time to float
            start_time = float(segment.get("start_time", 0))
            end_time = float(segment.get("end_time", 0))
            
            # Handle metadata
            metadata = segment.get("metadata", {})
            if metadata and "confidence" in metadata:
                metadata["confidence"] = float(metadata["confidence"])
            
            # Build the final segment dictionary
            final_segment = {
                "id": segment["id"],
                "video_id": segment["video_id"],
                "speaker_id": segment.get("speaker_id"),
                "text": segment["text"],
                "start_time": start_time,
                "end_time": end_time,
                "metadata": {
                    **metadata,
                    "word_count": len(segment["text"].split()),
                    "duration": end_time - start_time
                }
            }
            
            formatted_segments.append(final_segment)
            
        return formatted_segments
        
    except Exception as e:
        logger.error(f"Error getting video segments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video segments: {str(e)}"
        )

# Queue Routes
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

# Cleanup Routes
@router.post("/cleanup")
async def cleanup_storage(db: Session = Depends(get_db)) -> dict:
    """Clean up all storage files."""
    try:
        video_service = VideoService(db)
        video_count, audio_count = video_service.storage.cleanup_all()
        return {
            "status": "success",
            "message": f"Cleaned up {video_count} videos and {audio_count} audio files",
            "details": {
                "videos_removed": video_count,
                "audio_files_removed": audio_count
            }
        }
    except Exception as e:
        logger.error(f"Failed to cleanup storage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup storage: {str(e)}"
        )