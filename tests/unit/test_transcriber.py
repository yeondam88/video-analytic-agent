"""Unit tests for the transcriber module."""
import pytest
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import wave
import json
import os

from src.pipeline.stages.stage2_transcription.transcriber import DeepgramTranscriber
from src.pipeline.models import Video, VideoStatus, VideoSource

# Test data
TEST_VIDEO = {
    "id": 1,
    "url": "https://example.com/test.mp4",
    "source": VideoSource.LOOM,
    "source_id": "test-video-id",
    "title": "Test Video",
    "status": VideoStatus.AUDIO_EXTRACTED,
    "steps_completed": [],
    "processing_details": []
}

@pytest.fixture
def test_storage_path(tmp_path: Path) -> Path:
    """Create temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    audio_dir = storage_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir

@pytest.fixture
def mock_video():
    """Create a test video object."""
    return Video(**TEST_VIDEO)

@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    settings.services.DEEPGRAM_API_KEY = "test-api-key"
    return settings

@pytest.fixture
def transcriber(mock_settings):
    """Create a transcriber instance with mock settings."""
    return DeepgramTranscriber(settings=mock_settings)

@pytest.fixture
def mock_audio_file(test_storage_path):
    """Create a mock WAV file for testing."""
    audio_path = test_storage_path / "audio" / "test.wav"
    
    # Create a valid WAV file
    with wave.open(str(audio_path), 'wb') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(16000)  # 16kHz
        wav.writeframes(b'\x00' * 1000)  # Add some empty frames
    
    return audio_path

@pytest.mark.asyncio
class TestDeepgramTranscriber:
    async def test_validate_audio_format_success(self, transcriber, mock_audio_file):
        """Test successful audio format validation."""
        is_valid, message = await transcriber._validate_audio_format(mock_audio_file)
        assert is_valid
        assert "successful" in message

    async def test_validate_audio_format_failure(self, transcriber, test_storage_path):
        """Test audio format validation failure."""
        # Create invalid WAV file
        invalid_path = test_storage_path / "audio" / "invalid.wav"
        with wave.open(str(invalid_path), 'wb') as wav:
            wav.setnchannels(2)  # Stereo (invalid)
            wav.setsampwidth(2)
            wav.setframerate(44100)  # 44.1kHz (invalid)
            wav.writeframes(b'\x00' * 1000)
        
        is_valid, message = await transcriber._validate_audio_format(invalid_path)
        assert not is_valid
        assert "channels" in message

    async def test_validate_audio_file_success(self, transcriber, mock_audio_file):
        """Test successful audio file validation."""
        assert await transcriber._validate_audio_file(mock_audio_file)

    async def test_validate_audio_file_failure(self, transcriber, test_storage_path):
        """Test audio file validation failure."""
        non_existent = test_storage_path / "audio" / "nonexistent.wav"
        assert not await transcriber._validate_audio_file(non_existent)

    async def test_transcribe_success(self, transcriber, mock_video, mock_audio_file):
        """Test successful transcription."""
        mock_response = {
            'results': {
                'channels': [{
                    'alternatives': [{
                        'transcript': 'Test transcript',
                        'confidence': 0.95,
                        'words': [
                            {'word': 'Test', 'start': 0.0, 'end': 0.5},
                            {'word': 'transcript', 'start': 0.5, 'end': 1.0}
                        ]
                    }]
                }],
                'detected_language': 'ko',
                'language_confidence': 0.98
            },
            'metadata': {
                'duration': 1.0,
                'channels': 1,
                'created': '2024-02-16T00:00:00Z'
            }
        }
        
        # Mock Deepgram client
        mock_client = MagicMock()
        mock_client.transcription.prerecorded = AsyncMock(return_value=mock_response)
        
        with patch('deepgram.Deepgram', return_value=mock_client):
            result = await transcriber.transcribe(mock_video, mock_audio_file)
            
            assert result is not None
            assert result['results']['channels'][0]['alternatives'][0]['transcript'] == 'Test transcript'
            assert mock_video.status == VideoStatus.TRANSCRIBING

    async def test_transcribe_retry_success(self, transcriber, mock_video, mock_audio_file):
        """Test successful transcription after retry."""
        mock_response = {
            'results': {
                'channels': [{
                    'alternatives': [{
                        'transcript': 'Test transcript',
                        'confidence': 0.95
                    }]
                }]
            }
        }
        
        # Mock client that fails once then succeeds
        mock_client = MagicMock()
        mock_client.transcription.prerecorded = AsyncMock(
            side_effect=[asyncio.TimeoutError, mock_response]
        )
        
        with patch('deepgram.Deepgram', return_value=mock_client):
            result = await transcriber.transcribe(mock_video, mock_audio_file)
            
            assert result is not None
            assert mock_client.transcription.prerecorded.call_count == 2

    async def test_transcribe_failure(self, transcriber, mock_video, mock_audio_file):
        """Test transcription failure."""
        # Mock client that always fails
        mock_client = MagicMock()
        mock_client.transcription.prerecorded = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        with patch('deepgram.Deepgram', return_value=mock_client):
            result = await transcriber.transcribe(mock_video, mock_audio_file)
            
            assert result is None
            assert mock_video.status == VideoStatus.FAILED
            assert "API Error" in mock_video.error

    async def test_existing_transcription(self, transcriber, mock_video, mock_audio_file):
        """Test handling of existing transcription."""
        existing_transcription = {
            'video_id': mock_video.id,
            'raw_transcript': json.dumps({'results': {'transcript': 'Existing'}}),
            'extra_data': {}
        }
        
        # Mock database response
        mock_execute = AsyncMock(return_value=MagicMock(data=[existing_transcription]))
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_table)
        mock_table.eq = MagicMock(return_value=mock_table)
        mock_table.execute = mock_execute
        
        with patch('src.api.database.db.supabase.table', return_value=mock_table):
            result = await transcriber.transcribe(mock_video, mock_audio_file)
            
            assert result == existing_transcription 