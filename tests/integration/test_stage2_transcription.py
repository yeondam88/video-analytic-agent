"""Integration tests for stage 2 (transcription) of the video processing pipeline."""
import pytest
from pathlib import Path
import asyncio
import wave
import os
from loguru import logger

from src.pipeline.stages.stage1_download.downloader import VideoDownloader
from src.pipeline.stages.stage1_download.audio_extractor import AudioExtractor
from src.pipeline.stages.stage2_transcription.transcriber import DeepgramTranscriber
from src.pipeline.models import Video, VideoStatus, VideoSource
from src.config import settings

# Test video (use a short public video for testing)
TEST_VIDEO = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Short public video
    "source": VideoSource.YOUTUBE,
    "source_id": "dQw4w9WgXcQ",
    "title": "Test Video",
    "status": VideoStatus.PENDING,
    "steps_completed": [],
    "processing_details": []
}

@pytest.fixture
def test_storage_path(tmp_path: Path) -> Path:
    """Create temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    video_dir = storage_dir / "videos"
    audio_dir = storage_dir / "audio"
    video_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir

@pytest.fixture
def test_video():
    """Create a test video object."""
    return Video(**TEST_VIDEO)

@pytest.fixture
def downloader(test_storage_path):
    """Create a video downloader instance."""
    return VideoDownloader(video_dir=test_storage_path / "videos")

@pytest.fixture
def audio_extractor(test_storage_path):
    """Create an audio extractor instance."""
    return AudioExtractor(audio_dir=test_storage_path / "audio")

@pytest.fixture
def transcriber():
    """Create a transcriber instance."""
    return DeepgramTranscriber(settings=settings)

@pytest.mark.asyncio
async def test_stage2_pipeline(test_video, test_storage_path, downloader, audio_extractor, transcriber):
    """Test the complete stage 2 pipeline."""
    try:
        # Step 1: Download video
        logger.info("Step 1: Downloading video...")
        video_path = await downloader.download_video(test_video)
        assert video_path is not None
        assert video_path.exists()
        logger.info(f"Video downloaded to: {video_path}")
        
        # Step 2: Extract audio
        logger.info("Step 2: Extracting audio...")
        audio_path = await audio_extractor.extract_audio(test_video, video_path)
        assert audio_path is not None
        assert audio_path.exists()
        logger.info(f"Audio extracted to: {audio_path}")
        
        # Validate audio format
        with wave.open(str(audio_path), 'rb') as wav:
            assert wav.getnchannels() == 1  # Mono
            assert wav.getframerate() == 16000  # 16kHz
            assert wav.getsampwidth() == 2  # 16-bit
        
        # Step 3: Transcribe audio
        logger.info("Step 3: Transcribing audio...")
        transcription = await transcriber.transcribe(test_video, audio_path)
        assert transcription is not None
        
        # Validate transcription
        assert 'results' in transcription
        assert 'channels' in transcription['results']
        assert len(transcription['results']['channels']) > 0
        assert 'alternatives' in transcription['results']['channels'][0]
        assert len(transcription['results']['channels'][0]['alternatives']) > 0
        
        transcript = transcription['results']['channels'][0]['alternatives'][0]
        assert 'transcript' in transcript
        assert 'confidence' in transcript
        assert transcript['confidence'] > 0
        
        logger.info("Stage 2 pipeline test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stage 2 pipeline test failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            if video_path and video_path.exists():
                os.remove(video_path)
            if audio_path and audio_path.exists():
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_stage2_pipeline()) 