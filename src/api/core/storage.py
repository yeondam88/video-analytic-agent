import os
import aiohttp
import aiofiles
import ffmpeg
import logging
from typing import Tuple
import uuid
import shutil
from pathlib import Path
from loguru import logger

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.base_dir = Path("storage")
        self.videos_dir = self.base_dir / "videos"
        self.audio_dir = self.base_dir / "audio"
        
        # Ensure directories exist
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def get_video_path(self, video_id: str) -> Path:
        """Get path for video file."""
        return self.videos_dir / f"{video_id}.mp4"

    def get_audio_path(self, video_id: str) -> Path:
        """Get path for audio file."""
        return self.audio_dir / f"{video_id}.wav"

    def cleanup_files(self, video_id: str) -> bool:
        """Clean up video and audio files after processing."""
        try:
            video_path = self.get_video_path(video_id)
            audio_path = self.get_audio_path(video_id)
            
            # Delete video file if exists
            if video_path.exists():
                video_path.unlink()
                logger.info(f"Deleted video file for {video_id}")
            
            # Delete audio file if exists
            if audio_path.exists():
                audio_path.unlink()
                logger.info(f"Deleted audio file for {video_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup files for video {video_id}: {e}")
            return False

    def cleanup_all(self) -> tuple[int, int]:
        """Clean up all files in storage directories."""
        try:
            video_count = 0
            audio_count = 0
            
            # Clean videos directory
            for file in self.videos_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    video_count += 1
            
            # Clean audio directory
            for file in self.audio_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    audio_count += 1
            
            logger.info(f"Cleaned up {video_count} videos and {audio_count} audio files")
            return video_count, audio_count
        except Exception as e:
            logger.error(f"Failed to cleanup storage directories: {e}")
            return 0, 0

    async def download_video(self, url: str) -> str:
        """Download video from URL and return the local path."""
        video_id = str(uuid.uuid4())
        video_path = self.get_video_path(video_id)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download video: {response.status}")
                
                async with aiofiles.open(video_path, mode='wb') as f:
                    await f.write(await response.read())
                    
        return video_path
        
    async def extract_audio(self, video_path: str) -> str:
        """Extract audio from video and return the audio path."""
        video_id = video_path.stem
        audio_path = self.get_audio_path(video_id)
        
        try:
            # Extract audio using ffmpeg
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec='pcm_s16le',  # WAV format
                ac=1,                # Mono
                ar=16000             # 16kHz sample rate
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return audio_path
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise Exception(f"Failed to extract audio: {str(e)}")
            
    async def cleanup(self, *file_paths: str) -> None:
        """Clean up temporary files."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.error(f"Failed to remove file {path}: {str(e)}") 