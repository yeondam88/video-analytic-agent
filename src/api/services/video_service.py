from typing import Optional, Tuple, List
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
import re
import os
import uuid
import asyncio

from src.db.models import Video
from src.pipeline.types import VideoSource, VideoStatus
from src.api.core.storage import StorageService
from src.api.core.deepgram import DeepgramService
from src.api.core.openai import OpenAIService
from src.pipeline.video_processor import VideoProcessor
from src.pipeline.video.downloader import VideoDownloader

class VideoService:
    def __init__(self, db: Session):
        """Initialize video service."""
        self.db = db
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
                steps_completed=[]
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
        video_id: int,
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

    async def process_video(self, video_id: int) -> bool:
        """Process a video through the pipeline."""
        try:
            processor = VideoProcessor()
            success = await processor.process_video(video_id)
            return success
        except Exception as e:
            logger.error(f"Failed to process video {video_id}: {e}")
            return False

    def get_video(self, video_id: int) -> Optional[Video]:
        """Get a video by ID."""
        return self.db.query(Video).filter(Video.id == video_id).first()

    def list_videos(self, skip: int = 0, limit: int = 100) -> List[Video]:
        """List all videos with pagination."""
        return self.db.query(Video).offset(skip).limit(limit).all()

    def delete_video(self, video_id: int) -> bool:
        """Delete a video."""
        try:
            video = self.get_video(video_id)
            if not video:
                return False
            
            self.db.delete(video)
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete video: {e}")
            self.db.rollback()
            return False 