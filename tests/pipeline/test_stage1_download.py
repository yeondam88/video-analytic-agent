import pytest
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.pipeline.stages.stage1_download.downloader import VideoDownloader
from src.pipeline.stages.stage1_download.audio_extractor import AudioExtractor
from src.pipeline.models import Video, VideoStatus, VideoSource

# Test data
TEST_VIDEOS = [
    {
        "url": "https://www.loom.com/share/test-video-id",
        "source": VideoSource.LOOM,
        "source_id": "test-video-id",
        "title": "Test Loom Video",
        "status": VideoStatus.PENDING
    },
    {
        "url": "https://www.youtube.com/watch?v=test-video-id",
        "source": VideoSource.YOUTUBE,
        "source_id": "test-video-id",
        "title": "Test YouTube Video",
        "status": VideoStatus.PENDING
    }
]

@pytest.fixture
def test_storage_path(tmp_path: Path) -> Path:
    """Create temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    videos_dir = storage_dir / "videos"
    audio_dir = storage_dir / "audio"
    videos_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir

@pytest.fixture
def mock_video():
    """Create a test video object."""
    return Video(**TEST_VIDEOS[0])

@pytest.fixture
def downloader(test_storage_path):
    """Create a video downloader instance."""
    return VideoDownloader(video_dir=test_storage_path / "videos")

@pytest.fixture
def audio_extractor(test_storage_path):
    """Create an audio extractor instance."""
    return AudioExtractor(audio_dir=test_storage_path / "audio")

@pytest.mark.asyncio
async def test_video_download(downloader, mock_video, test_storage_path):
    """Test video download functionality."""
    # Mock successful download
    video_path = test_storage_path / "videos" / f"{mock_video.source_id}.mp4"
    video_path.touch()  # Create empty file
    
    with patch('src.pipeline.stages.stage1_download.downloader.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": mock_video.title,
            "duration": 60,
            "cdn_url": "https://example.com/video.mp4"
        }
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await downloader.download_video(mock_video)
        assert result is not None
        assert result.exists()
        assert result.name == f"{mock_video.source_id}.mp4"

@pytest.mark.asyncio
async def test_audio_extraction(audio_extractor, mock_video, test_storage_path):
    """Test audio extraction functionality."""
    # Create test video file
    video_path = test_storage_path / "videos" / f"{mock_video.source_id}.mp4"
    video_path.touch()
    
    with patch('src.pipeline.stages.stage1_download.audio_extractor.ffmpeg') as mock_ffmpeg:
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        
        result = await audio_extractor.extract_audio(mock_video, video_path)
        assert result is not None
        assert result.suffix == ".wav"
        mock_ffmpeg.output.assert_called_once()

@pytest.mark.asyncio
async def test_audio_format_validation(audio_extractor, test_storage_path):
    """Test audio format validation."""
    # Create test audio file
    audio_path = test_storage_path / "audio" / "test.wav"
    audio_path.touch()
    
    # Test format validation
    is_valid = await audio_extractor.validate_audio_format(audio_path)
    assert is_valid is False  # Empty file should fail validation

@pytest.mark.asyncio
async def test_full_download_process(downloader, audio_extractor, mock_video, test_storage_path):
    """Test the complete download and audio extraction process."""
    # Mock video download
    video_path = await downloader.download_video(mock_video)
    assert video_path is not None
    assert video_path.exists()
    
    # Mock audio extraction
    audio_path = await audio_extractor.extract_audio(mock_video, video_path)
    assert audio_path is not None
    assert audio_path.exists()
    assert audio_path.suffix == ".wav" 