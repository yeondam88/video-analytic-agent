"""Video processor module for handling video processing pipeline."""
from loguru import logger

from .coordinator import PipelineCoordinator
from .models import Video, VideoStatus
from src.api.database import db


class VideoProcessor:
    """Handles video processing through the pipeline."""
    
    def __init__(self):
        """Initialize the video processor with a pipeline coordinator."""
        self.coordinator = PipelineCoordinator()
    
    async def process_video(self, video_id: int) -> bool:
        """
        Process a video through the pipeline.
        
        Args:
            video_id: The ID of the video to process
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Start processing
            logger.info(f"Starting video processing for video {video_id}")
            success = await self.coordinator.process_video(video_id)
            
            if success:
                logger.info(f"Successfully processed video {video_id}")
            else:
                # Only log error if it's not already being processed
                response = db.supabase.table("videos").select("status").eq("id", video_id).execute()
                if response.data and response.data[0]["status"] != VideoStatus.PROCESSING:
                    logger.error(f"Failed to process video {video_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            # Update video status to failed
            try:
                await db.update("videos", video_id, {"status": VideoStatus.FAILED})
            except Exception as update_error:
                logger.error(f"Failed to update video status: {update_error}")
            return False 