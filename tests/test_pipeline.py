import pytest
from pathlib import Path
import asyncio
from loguru import logger
from unittest.mock import AsyncMock, MagicMock, patch

from src.pipeline.types import VideoStatus, VideoSource
from src.db.models import Video
from src.pipeline.coordinator import PipelineCoordinator
from src.pipeline.transcription.transcriber import DeepgramTranscriber
from src.api.database import db
from src.api.config.settings import Settings

# Test video URLs - one from Loom and one from YouTube
TEST_VIDEOS = [
    {
        "source": VideoSource.LOOM,
        "source_id": "c35d7c2936ad4f96b5f1e1a0f4b8e8c1",
        "url": "https://www.loom.com/share/c35d7c2936ad4f96b5f1e1a0f4b8e8c1",
        "title": "Test Loom Video"
    },
    {
        "source": VideoSource.YOUTUBE,
        "source_id": "dQw4w9WgXcQ",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "title": "Test YouTube Video"
    }
]

@pytest.fixture
def settings():
    """Create a new settings instance for each test"""
    return Settings(_env_file=".env")

@pytest.fixture
def test_storage_path(tmp_path: Path) -> Path:
    """Create a temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    videos_dir = storage_dir / "videos"
    audio_dir = storage_dir / "audio"
    videos_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir

@pytest.fixture
def test_video_url() -> str:
    """Return a test video URL."""
    return "https://www.loom.com/share/test-video-id"

@pytest.fixture
def test_video_data() -> dict:
    """Return test video data."""
    return {
        "source_id": "test-video-id",
        "source": VideoSource.LOOM,
        "url": "https://www.loom.com/share/test-video-id",
        "status": VideoStatus.PENDING,
        "title": "Test Video",
        "description": "This is a test video",
        "duration": 60,
        "thumbnail_url": "https://example.com/thumbnail.jpg",
        "to_process": True,
        "progress": 0.0,
        "steps_completed": [],
        "error": None
    }

@pytest.fixture
def mock_deepgram():
    """Mock Deepgram client."""
    with patch('src.pipeline.transcription.transcriber.Deepgram') as mock:
        mock_client = MagicMock()
        mock_client.transcription.prerecorded = AsyncMock(return_value={
            'results': {
                'channels': [
                    {
                        'alternatives': [
                            {
                                'transcript': 'This is a test transcript.',
                                'confidence': 0.95,
                                'words': [
                                    {
                                        'word': 'This',
                                        'start': 0.0,
                                        'end': 0.4,
                                        'confidence': 0.99
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        })
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_video_downloader(test_storage_path):
    """Mock video downloader."""
    with patch('src.pipeline.video.downloader.VideoDownloader') as mock:
        mock_instance = MagicMock()
        video_path = test_storage_path / "videos" / "test-video-id.mp4"
        video_path.parent.mkdir(parents=True, exist_ok=True)
        video_path.touch()  # Create an empty file
        mock_instance.download_video = AsyncMock(return_value=video_path)
        mock_instance.cleanup = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_audio_extractor(test_storage_path):
    """Mock audio extractor."""
    with patch('src.pipeline.audio.extractor.AudioExtractor') as mock:
        mock_instance = MagicMock()
        audio_path = test_storage_path / "audio" / "test-video-id.wav"
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        audio_path.touch()  # Create an empty file
        mock_instance.extract_audio = AsyncMock(return_value=audio_path)
        mock_instance.cleanup = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def transcriber(settings, mock_deepgram):
    """Return a transcriber instance."""
    return DeepgramTranscriber(settings)

@pytest.fixture
def coordinator(settings, transcriber, mock_video_downloader, mock_audio_extractor):
    """Create a coordinator with test settings"""
    return PipelineCoordinator(
        transcriber=transcriber,
        video_downloader=mock_video_downloader,
        audio_extractor=mock_audio_extractor
    )

@pytest.fixture
async def cleanup():
    """Clean up test videos after tests"""
    yield
    # Clean up database
    for video in TEST_VIDEOS:
        db.supabase.table("videos").delete().eq("source_id", video["source_id"]).execute()
    
    # Clean up files
    storage_dir = Path(__file__).parent.parent / "storage"
    for path in storage_dir.glob("**/*"):
        if path.is_file() and any(video["source_id"] in path.name for video in TEST_VIDEOS):
            path.unlink()

@pytest.fixture
def test_segment_data() -> dict:
    """Return test segment data."""
    return {
        "video_id": 1,
        "transcript": "This is a test transcript.",
        "summary": "Test summary",
        "embedding": [0.1, 0.2, 0.3]
    }

@pytest.fixture
def test_summary_data() -> dict:
    """Return test summary data."""
    return {
        "video_id": 1,
        "title": "Test Video",
        "summary": "This is a test summary.",
        "key_points": ["Point 1", "Point 2"],
        "action_items": ["Action 1", "Action 2"],
        "metadata": {
            "duration": 60,
            "speaker_count": 1
        }
    }

@pytest.mark.asyncio
async def test_pipeline(test_video_data=None):
    """Test the video processing pipeline."""
    # Create test video data
    if test_video_data is None:
        test_video_data = {
            "url": "https://www.loom.com/share/9fee16ced3574af3b3e017a1d643bd17?sid=44fa54f1-5b50-4233-a1f4-821bc8d82679",  # Shared private video
            "source": VideoSource.LOOM.value,
            "source_id": "9fee16ced3574af3b3e017a1d643bd17",
            "status": VideoStatus.PENDING.value,
            "progress": 0,
            "steps_completed": [],
            "processing_details": []
        }
    
    try:
        # Create video record
        video = db.supabase.table("videos").insert(test_video_data).execute()
        video_id = video.data[0]['id']
        logger.info(f"Created test video with ID: {video_id}")
        
        # Initialize pipeline
        coordinator = PipelineCoordinator()
        
        # Process video
        await coordinator.process_video(video_id)
        
        # Get final video status
        result = db.supabase.table("videos").select("*").eq("id", video_id).execute()
        final_video = result.data[0]
        
        logger.info(f"Final video status: {final_video['status']}")
        logger.info(f"Progress: {final_video['progress']}%")
        logger.info(f"Steps completed: {final_video['steps_completed']}")
        
        if final_video['status'] == VideoStatus.FAILED.value:
            logger.error(f"Error: {final_video.get('error', 'Unknown error')}")
            return False
        
        logger.info(f"Successfully processed {test_video_data['source']} video")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_pipeline()) 