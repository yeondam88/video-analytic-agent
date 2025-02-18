import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock, PropertyMock
import yt_dlp
import httpx
import contextlib
import tempfile
import shutil
import os

# Create a temporary directory for testing
TEST_DIR = Path(tempfile.mkdtemp())

# Mock the logger
mock_logger = MagicMock()

# Create a mock Supabase client
mock_execute = AsyncMock()
mock_execute.return_value = None
mock_eq = MagicMock()
mock_eq.execute = mock_execute
mock_update = MagicMock()
mock_update.eq = MagicMock(return_value=mock_eq)
mock_table = MagicMock()
mock_table.update = MagicMock(return_value=mock_update)
mock_client = MagicMock()
mock_client.table = MagicMock(return_value=mock_table)

# Mock the settings and database modules
mock_settings = Mock()
mock_settings.paths = Mock()
mock_settings.paths.VIDEO_DIR = TEST_DIR
mock_db = Mock(supabase=mock_client)

with patch.dict('sys.modules', {
    'src.api.database': Mock(db=mock_db),
    'src.config.settings': Mock(settings=mock_settings),
    'loguru': Mock(logger=mock_logger)
}):
    from src.pipeline.models import Video, VideoStatus, VideoSource, ProcessingStep
    from src.pipeline.video.downloader import VideoDownloader

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up temporary directory after each test."""
    yield
    shutil.rmtree(TEST_DIR, ignore_errors=True)

@pytest.fixture
def video_downloader():
    downloader = VideoDownloader()
    downloader.video_dir = TEST_DIR
    os.makedirs(TEST_DIR, exist_ok=True)
    return downloader

@pytest.fixture
def mock_video():
    return Video(
        id=1,
        source=VideoSource.LOOM,
        source_id="1234567890abcdef",
        url="https://www.loom.com/share/1234567890abcdef",
        status=VideoStatus.PENDING,
        steps_completed=[],
        processing_details=[]
    )

@pytest.fixture
def mock_youtube_video():
    return Video(
        id=2,
        source=VideoSource.YOUTUBE,
        source_id="dQw4w9WgXcQ",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        status=VideoStatus.PENDING,
        steps_completed=[],
        processing_details=[]
    )

class AsyncContextManagerMock:
    def __init__(self, mock_response):
        self.mock_response = mock_response

    async def __aenter__(self):
        return self.mock_response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class AsyncIteratorMock:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        data = self.data[self.index]
        self.index += 1
        return data

@pytest.mark.asyncio
class TestVideoDownloader:
    async def test_download_video_already_exists(self, video_downloader, mock_video):
        """Test skipping download if video already exists"""
        # Create a dummy file
        output_path = TEST_DIR / f"{mock_video.source_id}.mp4"
        output_path.touch()
        
        result = await video_downloader.download_video(mock_video)
        
        assert result is not None
        assert result.name == f"{mock_video.source_id}.mp4"
        assert mock_video.status == VideoStatus.DOWNLOADED
        mock_client.table.assert_called_with("videos")
        mock_table.update.assert_called()
        await mock_execute()

    async def test_download_loom_video_success(self, video_downloader, mock_video):
        """Test successful Loom video download"""
        mock_info = {
            'name': 'Test Video',
            'description': 'Test Description',
            'duration': 120,
            'thumbnail_url': 'https://example.com/thumbnail.jpg',
            'owner': {'name': 'Test User'},
            'created_at': '2024-01-01T00:00:00Z',
            'workspace': {'name': 'Test Workspace'},
            'cdn_url': 'https://example.com/video.mp4'
        }
        
        # Mock the response for video info
        mock_info_response = MagicMock()
        mock_info_response.raise_for_status = MagicMock()
        mock_info_response.json = MagicMock(return_value=mock_info)
        
        # Mock the response for video download
        mock_stream_response = MagicMock()
        mock_stream_response.raise_for_status = MagicMock()
        mock_stream_response.headers = {'content-length': '1000'}
        mock_stream_response.aiter_bytes = MagicMock(return_value=AsyncIteratorMock([b'test data']))
        
        # Create async context manager mocks
        mock_stream_context = AsyncContextManagerMock(mock_stream_response)
        mock_client_context = AsyncContextManagerMock(MagicMock(
            get=AsyncMock(return_value=mock_info_response),
            stream=MagicMock(return_value=mock_stream_context)
        ))
        
        # Create output path
        output_path = TEST_DIR / f"{mock_video.source_id}.mp4"
        
        with patch.object(httpx, 'AsyncClient', return_value=mock_client_context):
            result = await video_downloader.download_video(mock_video)
            
            assert result is not None
            assert result.name == f"{mock_video.source_id}.mp4"
            assert mock_video.status == VideoStatus.DOWNLOADED
            mock_client.table.assert_called_with("videos")
            mock_table.update.assert_called()
            await mock_execute()
            
            # Verify file was created
            assert output_path.exists()
            assert output_path.read_bytes() == b'test data'

    async def test_download_youtube_video_success(self, video_downloader, mock_youtube_video):
        """Test successful YouTube video download"""
        mock_info = {
            'title': 'Test Video',
            'description': 'Test Description',
            'duration': 120,
            'thumbnail': 'https://example.com/thumbnail.jpg',
            'uploader': 'Test User',
            'upload_date': '20240101',
            'view_count': 1000,
            'like_count': 100,
            'format': 'mp4'
        }
        
        # Mock yt-dlp
        mock_ydl = MagicMock()
        mock_ydl.extract_info = MagicMock(return_value=mock_info)
        mock_ydl.download = MagicMock()
        
        # Create output path
        output_path = TEST_DIR / f"{mock_youtube_video.source_id}.mp4"
        output_path.touch()  # Create the file as if yt-dlp downloaded it
        
        with patch('yt_dlp.YoutubeDL', return_value=mock_ydl):
            result = await video_downloader.download_video(mock_youtube_video)
            
            assert result is not None
            assert result.name == f"{mock_youtube_video.source_id}.mp4"
            assert mock_youtube_video.status == VideoStatus.DOWNLOADED
            mock_client.table.assert_called_with("videos")
            mock_table.update.assert_called()
            await mock_execute()
            
            # Verify file exists
            assert output_path.exists()

    async def test_download_video_failure(self, video_downloader, mock_video):
        """Test video download failure"""
        mock_client_context = AsyncContextManagerMock(MagicMock(
            get=AsyncMock(side_effect=Exception("Download failed"))
        ))
        
        with patch.object(httpx, 'AsyncClient', return_value=mock_client_context):
            result = await video_downloader.download_video(mock_video)
            
            assert result is None
            assert mock_video.status == VideoStatus.FAILED
            mock_client.table.assert_called_with("videos")
            mock_table.update.assert_called()
            await mock_execute()

    async def test_download_logs_progress(self, video_downloader, mock_video):
        """Test logging during download process"""
        mock_client_context = AsyncContextManagerMock(MagicMock(
            get=AsyncMock(side_effect=Exception("Download failed"))
        ))
        
        with patch.object(httpx, 'AsyncClient', return_value=mock_client_context):
            await video_downloader.download_video(mock_video)
            
            # Verify logging calls
            mock_logger.info.assert_any_call(f"Downloading Loom video {mock_video.source_id}")
            mock_logger.error.assert_any_call(f"Failed to download video {mock_video.source_id}: Download failed")
            mock_client.table.assert_called_with("videos")
            mock_table.update.assert_called()
            await mock_execute()

    async def test_update_video_metadata(self, video_downloader, mock_video):
        """Test video metadata update"""
        metadata = {
            'title': 'Test Video',
            'description': 'Test Description',
            'duration': 120,
            'thumbnail_url': 'https://example.com/thumbnail.jpg',
            'extra_data': {
                'uploader': 'Test User',
                'upload_date': '20240101'
            }
        }
        
        await video_downloader._update_video_metadata(mock_video, metadata)
        
        # Verify database update was called with correct data
        mock_client.table.assert_called_with("videos")
        mock_table.update.assert_called_with({
            'title': metadata['title'],
            'description': metadata['description'],
            'duration': metadata['duration'],
            'thumbnail_url': metadata['thumbnail_url'],
            'extra_data': metadata['extra_data']
        })
        await mock_execute() 