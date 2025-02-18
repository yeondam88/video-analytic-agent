"""Audio extractor module for extracting audio from videos."""
import os
from pathlib import Path
from typing import Optional, Tuple
import wave
import ffmpeg
from loguru import logger

from src.pipeline.models import Video, VideoStatus


class AudioExtractor:
    """Extracts audio from video files."""
    
    def __init__(self, audio_dir: Optional[Path] = None):
        """Initialize the audio extractor."""
        self.audio_dir = audio_dir or Path("storage/audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    async def extract_audio(self, video: Video, video_path: Path) -> Optional[Path]:
        """Extract audio from a video file."""
        try:
            # Create the output path
            audio_path = self.audio_dir / f"{video.source_id}.wav"
            
            # Skip if already extracted
            if audio_path.exists():
                # Validate existing audio file
                is_valid, message = await self.validate_audio_format(audio_path)
                if is_valid:
                    logger.info(f"Audio already extracted for video {video.source_id}")
                    return audio_path
                else:
                    logger.warning(f"Existing audio file invalid: {message}. Re-extracting...")
                    os.remove(audio_path)

            # Extract audio using ffmpeg
            logger.info(f"Extracting audio from video {video.source_id}")
            try:
                stream = ffmpeg.input(str(video_path))
                stream = ffmpeg.output(
                    stream,
                    str(audio_path),
                    acodec='pcm_s16le',  # WAV format
                    ac=1,                # Mono
                    ar=16000             # 16kHz sample rate
                )
                
                # Run the ffmpeg command
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
                
                # Validate the extracted audio
                is_valid, message = await self.validate_audio_format(audio_path)
                if not is_valid:
                    raise ValueError(f"Extracted audio validation failed: {message}")
                
                logger.info(f"Successfully extracted audio to {audio_path}")
                return audio_path
                
            except ffmpeg.Error as e:
                logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
                raise

        except Exception as e:
            logger.error(f"Failed to extract audio from video {video.source_id}: {e}")
            return None

    async def validate_audio_format(self, audio_path: Path) -> Tuple[bool, str]:
        """Validate audio file format meets requirements."""
        try:
            if not audio_path.exists():
                return False, f"Audio file does not exist: {audio_path}"
            
            if not audio_path.is_file():
                return False, f"Audio path is not a file: {audio_path}"
            
            with wave.open(str(audio_path), 'rb') as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                
                if channels != 1:
                    return False, f"Invalid audio channels: {channels} (must be mono)"
                if sample_rate != 16000:
                    return False, f"Invalid sample rate: {sample_rate}Hz (must be 16kHz)"
                if sample_width != 2:  # 16-bit
                    return False, f"Invalid bit depth: {sample_width*8}-bit (must be 16-bit)"
                
                # Check file size
                file_size = os.path.getsize(audio_path)
                if file_size == 0:
                    return False, "Audio file is empty"
                
                return True, "Audio format validation successful"
                
        except Exception as e:
            return False, f"Audio format validation failed: {str(e)}"

    async def cleanup(self, audio_path: str) -> None:
        """Clean up temporary audio file."""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.error(f"Failed to clean up audio file {audio_path}: {e}")
            raise 