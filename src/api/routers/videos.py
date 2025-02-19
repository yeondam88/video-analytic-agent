from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Path
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from loguru import logger
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import json
import re
import os
import shutil
import httpx

from src.api.database import get_db, db
from src.db.models import Video
from src.api.schemas.video import VideoCreate, VideoUpdate, VideoResponse, VideoSimilarityResponse
from src.api.services.video_service import VideoService
from src.pipeline.video_processor import VideoProcessor
from src.pipeline.types import VideoStatus, VideoSource

router = APIRouter()

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

class VideoProcessRequest(BaseModel):
    """Request model for video processing."""
    url: HttpUrl

class VideoRequest(BaseModel):
    """Request model for video creation."""
    url: HttpUrl

@router.post("/process", response_model=VideoResponse)
async def process_video(
    request: VideoProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process a video from a given URL."""
    try:
        # Create video entry
        service = VideoService(db)
        video = service.create_video(
            url=str(request.url),
            status=VideoStatus.PROCESSING  # Set initial status to PROCESSING
        )
        
        # Start processing in background
        processor = VideoProcessor()
        background_tasks.add_task(processor.process_video, video.id)
        
        logger.info(f"Started processing video {video.id} from URL: {request.url}")
        
        # Ensure all required fields are present
        current_time = datetime.utcnow()
        return VideoResponse(
            id=str(video.id),
            url=str(request.url),
            title=video.title or "Untitled Video",
            description=video.description or "",
            status=VideoStatus.PROCESSING.value,  # Use enum value
            error=None,
            progress=0.0,
            steps_completed=[],
            created_at=video.created_at or current_time,
            updated_at=video.updated_at or current_time,
            segments_count=0,
            has_summary=False
        )
    except Exception as e:
        logger.error(f"Failed to process video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )

@router.post("/", response_model=VideoResponse)
def create_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new video entry and start processing."""
    try:
        # Create video service
        service = VideoService(db)
        
        # Create video with URL
        video = service.create_video(url=str(request.url))
        
        # Start processing in background
        processor = VideoProcessor()
        background_tasks.add_task(processor.process_video, video.id)
        
        return VideoResponse(
            id=str(video.id),
            url=str(request.url),
            title=video.title,
            description=video.description,
            status=video.status.value,
            error=None,
            progress=0.0,
            steps_completed=[],
            created_at=video.created_at,
            updated_at=video.updated_at
        )
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create video: {str(e)}"
        )

@router.get("/", response_model=List[VideoResponse])
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """List all videos."""
    try:
        # Get videos directly from Supabase using global db module
        result = db.supabase.table("videos").select("*").order('created_at', desc=True).range(skip, skip + limit).execute()
        
        if not result.data:
            return []
            
        # Get current time for default values
        current_time = datetime.utcnow()
        
        # Convert videos to response format
        videos = []
        for video in result.data:
            # Generate thumbnail URL
            thumbnail_url = get_thumbnail_url(video["url"])
            logger.info(f"Generated thumbnail URL for video {video['id']}: {thumbnail_url}")
            
            # Handle timestamps with defaults
            created_at = video.get("created_at")
            if not created_at:
                created_at = current_time
            elif isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
            updated_at = video.get("updated_at")
            if not updated_at:
                updated_at = current_time
            elif isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            videos.append(VideoResponse(
                id=str(video["id"]),
                url=video["url"],
                title=video.get("title") or "Untitled Video",
                description=video.get("description", ""),
                thumbnail_url=thumbnail_url,
                status=video["status"],
                error=video.get("error"),
                progress=video.get("progress", 0.0),
                steps_completed=video.get("steps_completed", []),
                created_at=created_at,
                updated_at=updated_at,
                segments_count=0,
                has_summary=False
            ))
            
        return videos
        
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list videos: {str(e)}"
        )

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: str
):
    """Get a specific video by ID."""
    try:
        # Get video directly from Supabase using global db module
        result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Video with id {video_id} not found"
            )
            
        video = result.data[0]
        current_time = datetime.utcnow()
            
        return VideoResponse(
            id=str(video["id"]),
            url=video["url"],
            title=video["title"] or "Untitled Video",
            description=video.get("description", ""),
            status=video["status"],
            error=video.get("error"),
            progress=video.get("progress", 0.0),
            steps_completed=video.get("steps_completed", []),
            created_at=video.get("created_at", current_time),
            updated_at=video.get("updated_at", current_time),
            segments_count=0,
            has_summary=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
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
        from src.config import settings
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

@router.get("/{video_id}/segments", response_model=List[Dict[str, Any]])
async def get_video_segments(
    video_id: str,
) -> List[Dict[str, Any]]:
    """Get all segments for a specific video."""
    try:
        # Convert video_id to int for database query
        vid = int(video_id)
        
        # First verify the video exists
        video_result = db.supabase.table("videos").select("*").eq("id", vid).execute()
        if not video_result.data:
            raise HTTPException(status_code=404, detail="Video not found")
            
        # Fetch segments for the video
        result = db.supabase.table("segments") \
            .select("*") \
            .eq("video_id", str(vid)) \
            .is_("deleted_at", "null") \
            .order("start_time") \
            .execute()
            
        if not result.data:
            logger.warning(f"No segments found for video {video_id}")
            return []
            
        # Log segment count for debugging
        logger.info(f"Found {len(result.data)} segments for video {video_id}")
        
        # Transform the data to match frontend expectations
        segments = []
        for segment in result.data:
            segments.append({
                "id": str(segment["id"]),
                "video_id": str(segment["video_id"]),
                "start_time": float(segment["start_time"]),
                "end_time": float(segment["end_time"]),
                "text": segment["text"],
                "speaker_id": str(segment["speaker_id"]),
                "display_text": segment.get("display_text", segment["text"]),
                "metadata": segment.get("metadata", {}),
                "created_at": segment.get("created_at"),
                "updated_at": segment.get("updated_at")
            })
        
        return segments
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video ID format: {video_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get video segments: {str(e)}")
        logger.exception(e)  # Log full traceback
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video segments: {str(e)}"
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