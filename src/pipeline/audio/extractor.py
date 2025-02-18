"""Audio extractor module for extracting audio from videos."""
import os
from pathlib import Path
from typing import Optional

import ffmpeg
from loguru import logger

from src.config import settings
from src.db.database import db
from src.pipeline.models import Video, VideoStatus


class AudioExtractor:
    """Extracts audio from video files."""
    
    def __init__(self):
        """Initialize the audio extractor."""
        self.audio_dir = settings.paths.AUDIO_DIR
        os.makedirs(self.audio_dir, exist_ok=True)

    async def extract_audio(self, video: Video, video_path: Path) -> Optional[Path]:
        """Extract audio from a video file"""
        try:
            # Update video status
            video.status = VideoStatus.EXTRACTING_AUDIO
            await self._update_video_status(video)

            # Create the output path
            video_filename = Path(video_path).stem
            audio_path = str(self.audio_dir / f"{video_filename}.wav")
            
            # Skip if already extracted
            if os.path.exists(audio_path):
                logger.info(f"Audio already extracted for video {video.source_id}")
                return audio_path

            # Extract audio using ffmpeg
            logger.info(f"Extracting audio from video {video.source_id}")
            try:
                stream = ffmpeg.input(str(video_path))
                stream = ffmpeg.output(
                    stream,
                    audio_path,
                    acodec='pcm_s16le',  # WAV format
                    ac=1,                # Mono
                    ar=16000             # 16kHz sample rate
                )
                
                # Run the ffmpeg command
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
                
            except ffmpeg.Error as e:
                logger.error(f"FFmpeg error: {e.stderr.decode()}")
                raise

            logger.info(f"Successfully extracted audio to {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"Failed to extract audio from video {video.source_id}: {e}")
            video.status = VideoStatus.FAILED
            await self._update_video_status(video)
            return None

    async def _update_video_status(self, video: Video):
        """Update video status in the database"""
        try:
            data = {"status": video.status, "updated_at": "NOW()"}
            db.supabase.table("videos").update(data).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise

    async def cleanup(self, audio_path: str) -> None:
        """Clean up temporary audio file."""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.error(f"Failed to clean up audio file {audio_path}: {e}")
            raise 