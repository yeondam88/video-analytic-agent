"""Video downloader module for downloading videos from various sources."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
import yt_dlp
from loguru import logger

from src.pipeline.models import Video, VideoStatus
from src.pipeline.types import VideoSource


class VideoDownloader:
    """Downloads videos from various sources."""
    
    def __init__(self, video_dir: Optional[Path] = None):
        """Initialize the video downloader."""
        self.video_dir = video_dir or Path("storage/videos")
        os.makedirs(self.video_dir, exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'progress_hooks': [self._progress_hook],
        }

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp."""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                downloaded = d.get('downloaded_bytes', 0)
                progress = (downloaded / total) * 100
                logger.debug(f"Download progress: {progress:.1f}%")

    async def download_video(self, video: Video) -> Optional[Path]:
        """Download a video from its source."""
        try:
            # Create output path
            output_path = self.video_dir / f"{video.source_id}.mp4"
            
            # Skip if already downloaded
            if output_path.exists():
                logger.info(f"Video already downloaded: {video.source_id}")
                return output_path

            # Download video based on source
            if video.source == VideoSource.LOOM:
                return await self._download_loom(video, output_path)
            elif video.source == VideoSource.YOUTUBE:
                return await self._download_youtube(video, output_path)
            else:
                raise ValueError(f"Unsupported video source: {video.source}")
            
        except Exception as e:
            logger.error(f"Failed to download video {video.source_id}: {e}")
            return None

    async def _download_youtube(self, video: Video, output_path: Path) -> Optional[Path]:
        """Download a video from YouTube."""
        try:
            logger.info(f"Downloading YouTube video {video.source_id}")
            
            # Set output template for this video
            opts = dict(self.ydl_opts)
            opts['outtmpl'] = str(output_path)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract video info first
                info = ydl.extract_info(video.url, download=False)
                if not info:
                    raise ValueError(f"Could not extract video info for {video.source_id}")
                
                # Download the video
                logger.info(f"Starting download of {video.source_id}")
                ydl.download([video.url])
                
                if not output_path.exists():
                    raise FileNotFoundError(f"Failed to download video to {output_path}")
                
                logger.info(f"Successfully downloaded video to {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Failed to download YouTube video {video.source_id}: {e}")
            raise

    async def _download_loom(self, video: Video, output_path: Path) -> Optional[Path]:
        """Download a video from Loom."""
        try:
            video_id = video.source_id
            logger.info(f"Downloading Loom video {video_id}")
            
            # Configure HTTP client
            async with httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Origin": "https://www.loom.com",
                    "Referer": f"https://www.loom.com/share/{video_id}"
                }
            ) as client:
                # Get video info
                api_url = f"https://www.loom.com/v1/videos/{video_id}"
                response = await client.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                # Get video URL
                video_url = data.get("cdn_url")
                if not video_url:
                    raise ValueError("No video URL found in response")
                
                # Download video file
                logger.info(f"Downloading video from {video_url} to {output_path}")
                async with client.stream("GET", video_url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("content-length", 0))
                    
                    with open(output_path, "wb") as f:
                        downloaded = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                logger.debug(f"Download progress: {progress:.1f}%")
                
                # Return output path if file exists
                if output_path.exists():
                    logger.info(f"Successfully downloaded video to {output_path}")
                    return output_path
                
                logger.error(f"Failed to download video to {output_path}")
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error downloading Loom video {video_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to download Loom video {video_id}: {e}")
            raise

    async def cleanup(self, video_path: str) -> None:
        """Clean up temporary video file."""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Cleaned up video file: {video_path}")
        except Exception as e:
            logger.error(f"Failed to clean up video file {video_path}: {e}")
            raise 