import os
import aiohttp
import aiofiles
import ffmpeg
import logging
from typing import Tuple
import uuid

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.storage_dir = os.getenv("STORAGE_DIR", "storage")
        self.video_dir = os.path.join(self.storage_dir, "videos")
        self.audio_dir = os.path.join(self.storage_dir, "audio")
        
        # Create directories if they don't exist
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        
    async def download_video(self, url: str) -> str:
        """Download video from URL and return the local path."""
        video_id = str(uuid.uuid4())
        video_path = os.path.join(self.video_dir, f"{video_id}.mp4")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download video: {response.status}")
                
                async with aiofiles.open(video_path, mode='wb') as f:
                    await f.write(await response.read())
                    
        return video_path
        
    async def extract_audio(self, video_path: str) -> str:
        """Extract audio from video and return the audio path."""
        audio_id = str(uuid.uuid4())
        audio_path = os.path.join(self.audio_dir, f"{audio_id}.wav")
        
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