"""Test script for stage 1 of the video processing pipeline."""
import asyncio
from pathlib import Path
from loguru import logger

from src.pipeline.stages.stage1_download.downloader import VideoDownloader
from src.pipeline.stages.stage1_download.audio_extractor import AudioExtractor
from src.pipeline.models import Video, VideoStatus, VideoSource

# Test video (use a short public video for testing)
TEST_VIDEO = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Short public video
    "source": VideoSource.YOUTUBE,
    "source_id": "dQw4w9WgXcQ",
    "title": "Test Video",
    "status": VideoStatus.PENDING
}

async def test_stage1():
    """Test the complete stage 1 pipeline (download and audio extraction)."""
    try:
        # Create test directories
        base_dir = Path("test_storage")
        video_dir = base_dir / "videos"
        audio_dir = base_dir / "audio"
        video_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        downloader = VideoDownloader(video_dir=video_dir)
        audio_extractor = AudioExtractor(audio_dir=audio_dir)
        
        # Create video object
        video = Video(**TEST_VIDEO)
        logger.info(f"Testing with video: {video.url}")
        
        # Step 1: Download video
        logger.info("Step 1: Downloading video...")
        video_path = await downloader.download_video(video)
        if not video_path:
            raise ValueError("Failed to download video")
        logger.info(f"Video downloaded to: {video_path}")
        
        # Step 2: Extract audio
        logger.info("Step 2: Extracting audio...")
        audio_path = await audio_extractor.extract_audio(video, video_path)
        if not audio_path:
            raise ValueError("Failed to extract audio")
        logger.info(f"Audio extracted to: {audio_path}")
        
        # Step 3: Validate audio format
        logger.info("Step 3: Validating audio format...")
        is_valid, message = await audio_extractor.validate_audio_format(audio_path)
        if not is_valid:
            raise ValueError(f"Audio validation failed: {message}")
        logger.info(f"Audio validation successful: {message}")
        
        logger.info("Stage 1 pipeline test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stage 1 pipeline test failed: {e}")
        return False
    
    finally:
        # Cleanup test files
        try:
            if video_path and video_path.exists():
                await downloader.cleanup(str(video_path))
            if audio_path and audio_path.exists():
                await audio_extractor.cleanup(str(audio_path))
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_stage1()) 