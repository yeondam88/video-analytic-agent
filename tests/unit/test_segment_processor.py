"""Unit tests for the segment processor module."""
import pytest
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.pipeline.stages.stage3_segmentation.processor import SegmentProcessor
from src.pipeline.models import Video, VideoStatus, VideoSource, Segment

# Test data
TEST_VIDEO = {
    "id": 1,
    "url": "https://example.com/test.mp4",
    "source": VideoSource.LOOM,
    "source_id": "test-video-id",
    "title": "Test Video",
    "status": VideoStatus.TRANSCRIBED,
    "steps_completed": [],
    "processing_details": []
}

TEST_TRANSCRIPT = {
    "results": {
        "channels": [{
            "alternatives": [{
                "words": [
                    {"word": "Hello", "start": 0.0, "end": 0.5, "speaker": "A"},
                    {"word": "world", "start": 0.6, "end": 1.0, "speaker": "A"},
                    {"word": "this", "start": 2.0, "end": 2.2, "speaker": "B"},
                    {"word": "is", "start": 2.3, "end": 2.4, "speaker": "B"},
                    {"word": "a", "start": 2.5, "end": 2.6, "speaker": "B"},
                    {"word": "test", "start": 2.7, "end": 3.0, "speaker": "B"}
                ]
            }]
        }]
    }
}

@pytest.fixture
def mock_video():
    """Create a test video object."""
    return Video(**TEST_VIDEO)

@pytest.fixture
def mock_transcript():
    """Create a test transcript."""
    return TEST_TRANSCRIPT

@pytest.fixture
def processor():
    """Create a segment processor instance."""
    return SegmentProcessor()

@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        # Mock embeddings response
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create = AsyncMock(return_value=mock_embedding_response)
        
        # Mock chat completion response
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [
            MagicMock(message=MagicMock(content="Title\nSummary"))
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_chat_response)
        
        mock.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
class TestSegmentProcessor:
    async def test_process_transcript(self, processor, mock_video, mock_transcript, mock_openai):
        """Test processing a transcript into segments."""
        with patch('src.api.database.db.client.table') as mock_table:
            mock_table.return_value.insert = MagicMock(return_value=MagicMock(execute=AsyncMock()))
            mock_table.return_value.update = MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(execute=AsyncMock()))
            ))
            
            segments = await processor.process_transcript(mock_video, {"raw_transcript": json.dumps(mock_transcript)})
            
            assert segments is not None
            assert len(segments) == 2  # Two segments due to pause between speakers
            assert segments[0].speaker_id == "A"
            assert segments[1].speaker_id == "B"
            assert "Hello world" in segments[0].text
            assert "this is a test" in segments[1].text

    async def test_extract_segments(self, processor, mock_transcript):
        """Test extracting segments from transcript."""
        segments = await processor._extract_segments(mock_transcript)
        
        assert len(segments) == 2
        assert segments[0].start_time == 0.0
        assert segments[0].end_time == 1.0
        assert segments[1].start_time == 2.0
        assert segments[1].end_time == 3.0

    async def test_generate_embeddings(self, processor, mock_openai):
        """Test generating embeddings for segments."""
        segments = [
            Segment(
                video_id=1,
                start_time=0.0,
                end_time=1.0,
                text="Test segment",
                speaker_id="A"
            )
        ]
        
        await processor._generate_embeddings(segments)
        
        assert segments[0].embedding is not None
        assert len(segments[0].embedding) == 1536
        mock_openai.embeddings.create.assert_called_once()

    async def test_generate_summaries(self, processor, mock_openai):
        """Test generating summaries for segments."""
        segments = [
            Segment(
                video_id=1,
                start_time=0.0,
                end_time=1.0,
                text="This is a long test segment " * 10,  # Make it longer than 50 words
                speaker_id="A"
            )
        ]
        
        await processor._generate_summaries(segments)
        
        assert segments[0].title is not None
        assert segments[0].display_text is not None
        assert segments[0].segment_metadata.get("has_summary") is True
        mock_openai.chat.completions.create.assert_called_once()

    async def test_save_segments(self, processor):
        """Test saving segments to database."""
        segments = [
            Segment(
                video_id=1,
                start_time=0.0,
                end_time=1.0,
                text="Test segment",
                speaker_id="A",
                embedding=[0.1] * 1536
            )
        ]
        
        with patch('src.api.database.db.client.table') as mock_table:
            mock_insert = MagicMock(execute=AsyncMock())
            mock_table.return_value.insert = MagicMock(return_value=mock_insert)
            
            await processor._save_segments(segments)
            
            mock_table.assert_called_with("segments")
            mock_table.return_value.insert.assert_called_once()
            mock_insert.execute.assert_called_once()

    async def test_update_video_status(self, processor, mock_video):
        """Test updating video status."""
        with patch('src.api.database.db.client.table') as mock_table:
            mock_execute = AsyncMock()
            mock_eq = MagicMock(execute=mock_execute)
            mock_update = MagicMock(eq=MagicMock(return_value=mock_eq))
            mock_table.return_value.update = MagicMock(return_value=mock_update)
            
            await processor._update_video_status(mock_video)
            
            mock_table.assert_called_with("videos")
            mock_table.return_value.update.assert_called_once()
            mock_execute.assert_called_once()

    async def test_error_handling(self, processor, mock_video, mock_transcript):
        """Test error handling during processing."""
        with patch('src.api.database.db.client.table') as mock_table:
            mock_table.return_value.insert = MagicMock(side_effect=Exception("Database error"))
            
            with pytest.raises(Exception):
                await processor.process_transcript(mock_video, {"raw_transcript": json.dumps(mock_transcript)})
            
            assert mock_video.status == VideoStatus.FAILED

    async def test_progress_tracking(self, processor, mock_video, mock_transcript, mock_openai):
        """Test progress tracking during processing."""
        with patch('src.api.database.db.client.table') as mock_table:
            mock_execute = AsyncMock()
            mock_eq = MagicMock(execute=mock_execute)
            mock_update = MagicMock(eq=MagicMock(return_value=mock_eq))
            mock_table.return_value.update = MagicMock(return_value=mock_update)
            mock_table.return_value.insert = MagicMock(return_value=MagicMock(execute=AsyncMock()))
            
            await processor.process_transcript(mock_video, {"raw_transcript": json.dumps(mock_transcript)})
            
            # Verify progress updates were made
            progress_updates = [call[0][0] for call in mock_table.return_value.update.call_args_list 
                              if 'progress' in call[0][0]]
            assert len(progress_updates) > 0 