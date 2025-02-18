from typing import Optional, List, Dict, Any
from loguru import logger
import asyncio
from datetime import datetime
from pathlib import Path

from src.pipeline.models import Video, VideoStatus, ProcessingStep
from src.pipeline.video.downloader import VideoDownloader
from src.pipeline.audio.extractor import AudioExtractor
from src.pipeline.transcription.transcriber import DeepgramTranscriber
from src.pipeline.segmentation.processor import SegmentProcessor
from src.api.database import db
from src.config import settings


class PipelineCoordinator:
    """Coordinates the video processing pipeline."""
    
    def __init__(self):
        """Initialize the pipeline coordinator."""
        self.downloader = VideoDownloader()
        self.audio_extractor = AudioExtractor()
        self.transcriber = DeepgramTranscriber()
        self.segmenter = SegmentProcessor()
        
    async def process_video(self, video_id: int) -> bool:
        """Process a video through the pipeline."""
        video = None
        try:
            # Get video from database
            result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
            if not result.data:
                raise ValueError(f"Video not found: {video_id}")
            
            video = Video(**result.data[0])
            logger.info(f"Processing video {video.id} ({video.source_id})")
            
            # Download video
            if not await self._execute_step(video, "download", self._download_video):
                return False
            
            # Extract audio
            if not await self._execute_step(video, "extract_audio", self._extract_audio):
                return False
            
            # Transcribe audio
            if not await self._execute_step(video, "transcribe", self._transcribe_audio):
                return False
            
            # Get transcription data
            transcription_result = db.supabase.table("transcriptions").select("*").eq("video_id", str(video.id)).execute()
            if not transcription_result.data:
                logger.error(f"No transcription found for video {video.id}")
                self._update_progress(video, VideoStatus.FAILED, 0, "transcription_failed", "No transcription data found")
                return False
            
            transcript_data = transcription_result.data[0]["raw_response"]
            
            # Segment video
            if not await self._execute_step(video, "segment", lambda v: self._segment_video(v, transcript_data)):
                return False
            
            # Mark as completed
            video.status = VideoStatus.COMPLETED
            self._update_progress(video, VideoStatus.COMPLETED, 100, "processing_completed")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to process video {video_id}: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)  # Log full traceback
            try:
                # Update video status and error message
                if video:
                    video.status = VideoStatus.FAILED
                    video.error = error_msg
                    self._update_progress(video, VideoStatus.FAILED, 0, "processing_failed", error_msg)
                else:
                    # If video object not created, update directly in database
                    db.supabase.table("videos").update({
                        "status": VideoStatus.FAILED.value,
                        "error": error_msg,
                        "progress": 0
                    }).eq("id", video_id).execute()
            except Exception as update_error:
                logger.error(f"Failed to update video status: {update_error}")
                logger.exception(update_error)
            return False
    
    def _update_progress(self, video: Video, status: VideoStatus, progress: float, step: str, error: Optional[str] = None) -> None:
        """Update video progress in database."""
        try:
            # Get current steps
            result = db.supabase.table("videos").select("steps_completed").eq("id", video.id).execute()
            if not result.data:
                raise ValueError(f"Video not found: {video.id}")
            
            current_video = result.data[0]
            steps = current_video.get("steps_completed", [])
            
            # Add new step if not already present
            if step not in steps:
                steps.append(step)
            
            # Update video
            data = {
                "status": status.value,
                "progress": progress,
                "steps_completed": steps
            }
            
            if error:
                data["error"] = error
            
            db.supabase.table("videos").update(data).eq("id", video.id).execute()
            
            logger.info(f"Video {video.id} - {step} - {status} ({progress}%)")
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            raise
    
    async def _execute_step(self, video: Video, step: str, func) -> bool:
        """Execute a pipeline step with retries."""
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Update progress for step start
                self._update_progress(
                    video,
                    VideoStatus.PROCESSING,
                    self._calculate_progress(step, attempt),
                    f"{step}_started"
                )
                
                # Execute step
                result = await func(video)
                if result:
                    # Update progress for step completion
                    self._update_progress(
                        video,
                        VideoStatus.PROCESSING,
                        self._calculate_progress(step, attempt),
                        f"{step}_completed"
                    )
                    return True
                else:
                    # Step failed but didn't raise an exception
                    error_msg = f"{step} step failed without error"
                    logger.error(error_msg)
                    self._update_progress(
                        video,
                        VideoStatus.FAILED,
                        self._calculate_progress(step, attempt),
                        f"{step}_failed",
                        error_msg
                    )
                    return False
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"{step} step failed for video {video.id} (attempt {attempt + 1}/{max_retries}): {e}")
                logger.exception(e)
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    error_msg = f"Failed to {step} video after {max_retries} attempts: {last_error}"
                    video.status = VideoStatus.FAILED
                    video.error = error_msg
                    self._update_progress(
                        video,
                        VideoStatus.FAILED,
                        self._calculate_progress(step, attempt),
                        f"{step}_failed",
                        error_msg
                    )
                    return False
                
                # Wait before retrying with exponential backoff
                await asyncio.sleep(min(2 ** attempt, 30))
        
        return False
    
    async def _download_video(self, video: Video) -> bool:
        """Download the video."""
        try:
            output_path = await self.downloader.download_video(video)
            return output_path is not None
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return False
    
    async def _extract_audio(self, video: Video) -> bool:
        """Extract audio from the video."""
        try:
            # Get video path
            video_path = Path(settings.paths.VIDEO_DIR) / f"{video.source_id}.mp4"
            if not video_path.exists():
                logger.error(f"Video file not found: {video_path}")
                return False
                
            output_path = await self.audio_extractor.extract_audio(video, video_path)
            return output_path is not None
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            return False
    
    async def _transcribe_audio(self, video: Video) -> bool:
        """Transcribe the audio."""
        try:
            # Get audio path
            audio_path = Path(settings.paths.AUDIO_DIR) / f"{video.source_id}.wav"
            if not audio_path.exists():
                logger.error(f"Audio file not found: {audio_path}")
                return False
                
            transcription = await self.transcriber.transcribe(video, audio_path)
            return transcription is not None
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return False
    
    async def _segment_video(self, video: Video, transcript_data: dict) -> bool:
        """Segment video based on transcript."""
        try:
            logger.info(f"Starting segmentation for video {video.id}")
            
            # Update video status
            self._update_progress(
                video,
                VideoStatus.SEGMENTING,
                self._calculate_progress("segment", 0),
                "segmentation_started"
            )
            
            # Process segments using the new segmentation processor
            segments = await self.segmenter.process_transcript(video.id, transcript_data)
            
            if not segments:
                logger.error(f"No segments created for video {video.id}")
                return False
                
            logger.info(f"Created {len(segments)} segments for video {video.id}")
            
            # Update progress
            self._update_progress(
                video,
                VideoStatus.PROCESSING,
                self._calculate_progress("segment", 2),
                "segmentation_completed"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to segment video {video.id}: {e}")
            return False
    
    def _calculate_progress(self, step: str, attempt: int) -> float:
        """Calculate progress percentage for a step."""
        step_weights = {
            "download": 15,
            "extract_audio": 20,
            "transcribe": 30,
            "segment": 35
        }
        
        steps = list(step_weights.keys())
        current_step_index = steps.index(step)
        
        # Calculate progress up to current step
        progress = sum(step_weights[s] for s in steps[:current_step_index])
        
        # Add progress for current step
        current_step_progress = step_weights[step] * ((attempt + 1) / 3)  # Divide by max retries
        progress += current_step_progress
        
        return progress
    
    async def _cleanup_files(self, video_path: Optional[str], audio_path: Optional[str]) -> None:
        """Clean up temporary files."""
        try:
            if video_path:
                await self.downloader.cleanup(str(video_path))
            if audio_path:
                await self.audio_extractor.cleanup(str(audio_path))
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")
            raise 