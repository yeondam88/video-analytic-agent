from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
import re
import os
import uuid
import asyncio

from src.db.models.video import Video
from src.pipeline.types import VideoSource, VideoStatus
from src.api.core.storage import StorageService
from src.api.core.deepgram import DeepgramService
from src.api.core.openai import OpenAIService
from src.pipeline.video_processor import VideoProcessor
from src.pipeline.video.downloader import VideoDownloader
from src.api.database import db

class VideoService:
    def __init__(self, db_session: Session):
        """Initialize video service."""
        self.db = db_session
        self.storage = StorageService()
        self.deepgram = DeepgramService()
        self.openai = OpenAIService()

    def extract_video_info(self, url: str) -> Tuple[VideoSource, str]:
        """Extract source and source_id from URL."""
        try:
            # Use VideoDownloader's parse_video_url method
            source, source_id = VideoDownloader.parse_video_url(url)
            return source, source_id
        except ValueError as e:
            logger.error(f"Failed to parse video URL: {e}")
            raise

    def create_video(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        status: VideoStatus = VideoStatus.PENDING,
        duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Video:
        """Create a new video entry."""
        try:
            # Extract source and source_id from URL
            source, source_id = self.extract_video_info(url)
            
            # Create video object
            video = Video(
                source=source,
                source_id=source_id,
                url=url,
                title=title,
                description=description,
                thumbnail_url=thumbnail_url,
                status=status,
                duration=duration,
                progress=0.0,
                steps_completed=[],
                extra_data=metadata or {}
            )
            
            # Save to database
            self.db.add(video)
            self.db.commit()
            self.db.refresh(video)
            
            logger.info(f"Created video entry: {video.id}")
            return video
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            self.db.rollback()
            raise

    def update_video_progress(
        self,
        video_id: str,
        status: VideoStatus,
        progress: float,
        step: str,
        error: Optional[str] = None
    ) -> None:
        """Update video processing progress."""
        try:
            video = self.get_video(video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")
            
            # Update progress
            video.status = status
            video.progress = progress
            if step not in (video.steps_completed or []):
                video.steps_completed = (video.steps_completed or []) + [step]
            if error:
                video.error = error
            
            self.db.commit()
            logger.info(f"Updated video {video_id} progress: {progress}%")
            
        except Exception as e:
            logger.error(f"Failed to update video progress: {e}")
            self.db.rollback()
            raise

    async def process_video(self, video_id: str) -> bool:
        """Process a video through the pipeline."""
        try:
            logger.info(f"Starting video processing for video {video_id}")
            processor = VideoProcessor()
            success = await processor.process_video(video_id)
            
            if success:
                logger.info(f"Video {video_id} processed successfully, starting cleanup")
                # Get video data to ensure we have the correct source_id
                video_data = self.get_video(video_id)
                if not video_data:
                    logger.error(f"Could not find video {video_id} for cleanup")
                    return False
                    
                # Use source_id for cleanup since that's what we use for file names
                source_id = video_data.get("source_id")
                if not source_id:
                    logger.error(f"No source_id found for video {video_id}")
                    return False
                    
                # Clean up storage files after successful processing
                cleanup_success = self.storage.cleanup_files(source_id)
                if not cleanup_success:
                    logger.warning(f"Failed to cleanup storage files for video {video_id} (source_id: {source_id})")
                
            return success
        except Exception as e:
            logger.error(f"Failed to process video {video_id}: {e}")
            logger.exception(e)  # Log full traceback
            return False

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get a video by ID with all its data."""
        try:
            # Get video from Supabase
            result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
            if not result.data:
                return None
                
            video_data = result.data[0]
            
            # Get segments count
            segments_result = db.supabase.table("segments").select("count").eq("video_id", video_id).execute()
            video_data['segments_count'] = segments_result.count if segments_result.count is not None else 0
            
            return video_data
            
        except Exception as e:
            logger.error(f"Failed to get video {video_id}: {e}")
            raise

    def get_video_segments(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all segments for a video."""
        try:
            result = db.supabase.table("segments") \
                .select("*") \
                .eq("video_id", video_id) \
                .is_("deleted_at", "null") \
                .order("start_time") \
                .execute()
                
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get segments for video {video_id}: {e}")
            raise

    def list_videos(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List all videos with pagination."""
        try:
            result = db.supabase.table("videos") \
                .select("*") \
                .order("created_at", desc=True) \
                .range(skip, skip + limit) \
                .execute()
                
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to list videos: {e}")
            raise

    def delete_video(self, video_id: str) -> bool:
        """Delete a video and its associated data."""
        try:
            # Delete segments
            db.supabase.table("segments").delete().eq("video_id", video_id).execute()
            
            # Delete transcriptions
            db.supabase.table("transcriptions").delete().eq("video_id", video_id).execute()
            
            # Delete video
            result = db.supabase.table("videos").delete().eq("id", video_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to delete video: {e}")
            return False 