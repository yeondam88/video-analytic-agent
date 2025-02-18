"""Video downloader module for downloading videos from various sources."""
import os
import re
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from loguru import logger
import httpx

from src.config import settings
from src.api.database import db
from src.pipeline.models import Video, VideoStatus
from src.pipeline.types import VideoSource


class VideoDownloader:
    """Downloads videos from various sources."""
    
    def __init__(self):
        """Initialize the video downloader."""
        self.video_dir = settings.paths.VIDEO_DIR
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
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }
        
        # Configure HTTP client for Loom
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://www.loom.com',
            },
            follow_redirects=True
        )

    @staticmethod
    def parse_video_url(url: str) -> Tuple[VideoSource, str]:
        """
        Parse video URL to determine source and extract video ID.
        
        Args:
            url: The video URL to parse
            
        Returns:
            Tuple[VideoSource, str]: The video source and ID
            
        Raises:
            ValueError: If the URL is invalid or unsupported
        """
        # YouTube URL patterns
        youtube_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
        ]
        
        # Loom URL patterns
        loom_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?loom\.com\/share\/([a-zA-Z0-9]+)',
            r'(?:https?:\/\/)?(?:www\.)?loom\.com\/embed\/([a-zA-Z0-9]+)'
        ]
        
        # Try YouTube patterns
        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                return VideoSource.YOUTUBE, match.group(1)
        
        # Try Loom patterns - strip any query parameters first
        base_url = url.split('?')[0]
        for pattern in loom_patterns:
            match = re.match(pattern, base_url)
            if match:
                return VideoSource.LOOM, match.group(1)
        
        raise ValueError(f"Unsupported video URL format: {url}")

    def _progress_hook(self, d):
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
            # Update video status to downloading
            video.status = VideoStatus.DOWNLOADING
            await self._update_video_status(video)
            
            # Create output path
            output_path = Path(self.video_dir) / f"{video.source_id}.mp4"
            
            # Skip if already downloaded
            if output_path.exists():
                logger.info(f"Video already downloaded: {video.source_id}")
                video.status = VideoStatus.DOWNLOADED
                await self._update_video_status(video)
                return output_path
            
            # Download video based on source
            if video.source == VideoSource.LOOM:
                output_path = await self._download_loom(video, output_path)
            elif video.source == VideoSource.YOUTUBE:
                output_path = await self._download_youtube(video, output_path)
            else:
                raise ValueError(f"Unsupported video source: {video.source}")
            
            if output_path and output_path.exists():
                # Update video status to downloaded
                video.status = VideoStatus.DOWNLOADED
                await self._update_video_status(video)
                logger.info(f"Successfully downloaded video {video.source_id}")
                return output_path
            
            logger.error(f"Failed to download video {video.source_id}")
            video.status = VideoStatus.FAILED
            await self._update_video_status(video)
            return None
            
        except Exception as e:
            logger.error(f"Failed to download video {video.source_id}: {e}")
            # Update video status to failed
            video.status = VideoStatus.FAILED
            await self._update_video_status(video)
            return None

    async def _download_youtube(self, video: Video, output_path: Path) -> Optional[Path]:
        """Download a video from YouTube"""
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
                
                # Update video metadata
                metadata = {
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'thumbnail_url': info.get('thumbnail'),
                    'extra_data': {
                        'uploader': info.get('uploader'),
                        'upload_date': info.get('upload_date'),
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'format': info.get('format')
                    }
                }
                await self._update_video_metadata(video, metadata)
                
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
            
            # Extract session ID if present
            session_id = None
            url_match = re.match(r'.*\?sid=([a-zA-Z0-9-]+)', video.url)
            if url_match:
                session_id = url_match.group(1)
            
            # Configure HTTP client
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://www.loom.com",
                "Referer": f"https://www.loom.com/share/{video_id}"
            }
            
            if session_id:
                headers["Cookie"] = f"loom_session_id={session_id}"
            
            async with httpx.AsyncClient(
                timeout=30.0,
                headers=headers,
                follow_redirects=True
            ) as client:
                # First try to get video info
                api_url = f"https://www.loom.com/v1/videos/{video_id}"
                logger.info(f"Fetching video info from: {api_url}")
                
                try:
                    response = await client.get(api_url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Get video URL and metadata
                    video_url = data.get("cdn_url")
                    if not video_url:
                        raise ValueError("No video URL found in response")
                    
                    # Update video metadata
                    metadata = {
                        'title': data.get('name'),
                        'description': data.get('description'),
                        'duration': data.get('duration'),
                        'thumbnail_url': data.get('thumbnail_url'),
                        'extra_data': {
                            'owner': data.get('owner', {}).get('name'),
                            'created_at': data.get('created_at'),
                            'workspace': data.get('workspace', {}).get('name')
                        }
                    }
                    await self._update_video_metadata(video, metadata)
                    
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
                    logger.error(f"Failed to get video URL: {e}")
                    raise ValueError("Download failed")
                
        except Exception as e:
            logger.error(f"Failed to download Loom video {video_id}: {e}")
            raise

    async def _update_video_status(self, video: Video):
        """Update video status in the database"""
        try:
            db.supabase.table("videos").update({
                "status": video.status.value
            }).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
            raise

    async def _update_video_metadata(self, video: Video, metadata: dict):
        """Update video metadata in the database"""
        try:
            update_data = {
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "duration": metadata.get("duration"),
                "thumbnail_url": metadata.get("thumbnail_url"),
                "extra_data": metadata.get("extra_data", {})
            }
            db.supabase.table("videos").update(update_data).eq("id", video.id).execute()
        except Exception as e:
            logger.error(f"Failed to update video metadata: {e}")
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