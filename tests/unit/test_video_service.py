import pytest
from unittest.mock import Mock, patch
from src.api.services.video_service import VideoService
from src.pipeline.models import Video, VideoStatus, VideoSource

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def video_service(mock_db):
    return VideoService(mock_db)

class TestVideoService:
    def test_extract_loom_info_share_url(self, video_service):
        """Test extracting info from standard share URL"""
        url = "https://www.loom.com/share/1234567890abcdef"
        video_id, share_url = video_service.extract_loom_info(url)
        assert video_id == "1234567890abcdef"
        assert share_url == url

    def test_extract_loom_info_embed_url(self, video_service):
        """Test extracting info from embed URL"""
        url = "https://www.loom.com/embed/1234567890abcdef"
        video_id, share_url = video_service.extract_loom_info(url)
        assert video_id == "1234567890abcdef"
        assert share_url == "https://www.loom.com/share/1234567890abcdef"

    def test_extract_loom_info_short_url(self, video_service):
        """Test extracting info from short URL"""
        url = "https://loom.com/v/1234567890abcdef"
        video_id, share_url = video_service.extract_loom_info(url)
        assert video_id == "1234567890abcdef"
        assert share_url == "https://www.loom.com/share/1234567890abcdef"

    def test_extract_loom_info_invalid_url(self, video_service):
        """Test extracting info from invalid URL"""
        invalid_urls = [
            "https://loom.com/invalid/1234567890abcdef",
            "https://other-site.com/video",
            "not-a-url",
            "https://www.loom.com/",
            "https://loom.com"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError) as exc_info:
                video_service.extract_loom_info(url)
            assert "Invalid Loom URL format" in str(exc_info.value)

    def test_create_video_success(self, video_service, mock_db):
        """Test successful video creation"""
        url = "https://www.loom.com/share/1234567890abcdef"
        video = video_service.create_video(url=url)
        
        assert video.source == VideoSource.LOOM
        assert video.source_id == "1234567890abcdef"
        assert video.url == url
        assert video.status == VideoStatus.PENDING
        assert video.to_process is True
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_video_with_metadata(self, video_service, mock_db):
        """Test video creation with metadata"""
        url = "https://www.loom.com/share/1234567890abcdef"
        title = "Test Video"
        description = "Test Description"
        thumbnail_url = "https://example.com/thumbnail.jpg"
        duration = 120
        
        video = video_service.create_video(
            url=url,
            title=title,
            description=description,
            thumbnail_url=thumbnail_url,
            duration=duration
        )
        
        assert video.source == VideoSource.LOOM
        assert video.source_id == "1234567890abcdef"
        assert video.url == url
        assert video.title == title
        assert video.description == description
        assert video.thumbnail_url == thumbnail_url
        assert video.duration == duration
        assert video.status == VideoStatus.PENDING
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_video_database_error(self, video_service, mock_db):
        """Test video creation with database error"""
        url = "https://www.loom.com/share/1234567890abcdef"
        mock_db.commit.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            video_service.create_video(url=url)
        
        assert "Database error" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    @patch('src.api.services.video_service.logger')
    def test_create_video_logs_error(self, mock_logger, video_service, mock_db):
        """Test error logging during video creation"""
        url = "https://www.loom.com/share/1234567890abcdef"
        error_message = "Database error"
        mock_db.commit.side_effect = Exception(error_message)
        
        with pytest.raises(Exception):
            video_service.create_video(url=url)
        
        mock_logger.error.assert_called_once()
        assert error_message in mock_logger.error.call_args[0][0] 