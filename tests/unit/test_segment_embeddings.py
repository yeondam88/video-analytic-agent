"""Unit tests for segment embedding and summary generation."""
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

# Test segments with varying lengths and content
TEST_SEGMENTS = [
    {
        "video_id": 1,
        "start_time": 0.0,
        "end_time": 10.0,
        "text": "This is a short test segment.",
        "speaker_id": "A"
    },
    {
        "video_id": 1,
        "start_time": 10.0,
        "end_time": 30.0,
        "text": "This is a longer test segment that should receive a summary. " * 5,  # > 50 words
        "speaker_id": "B"
    },
    {
        "video_id": 1,
        "start_time": 30.0,
        "end_time": 40.0,
        "text": "This segment contains technical terms: API, JSON, HTTP, REST.",
        "speaker_id": "A"
    }
]

@pytest.fixture
def mock_video():
    """Create a test video object."""
    return Video(**TEST_VIDEO)

@pytest.fixture
def test_segments():
    """Create test segment objects."""
    return [Segment(**segment) for segment in TEST_SEGMENTS]

@pytest.fixture
def processor():
    """Create a segment processor instance."""
    return SegmentProcessor()

@pytest.fixture
def mock_openai():
    """Mock OpenAI client with realistic responses."""
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        
        # Mock embeddings response
        async def mock_create_embedding(*args, **kwargs):
            # Generate realistic-looking embeddings
            response = MagicMock()
            response.data = [
                MagicMock(embedding=[0.1 * i for i in range(1536)])  # 1536-dimensional vector
                for _ in range(len(kwargs.get('input', [''])))
            ]
            return response
            
        mock_client.embeddings.create = AsyncMock(side_effect=mock_create_embedding)
        
        # Mock chat completion response with realistic titles and summaries
        async def mock_create_completion(*args, **kwargs):
            response = MagicMock()
            messages = kwargs.get('messages', [])
            text = next(msg['content'] for msg in messages if msg['role'] == 'user')
            
            if 'technical terms' in text.lower():
                response.choices = [MagicMock(
                    message=MagicMock(
                        content="Technical API Overview\nA concise explanation of various technical terms and protocols."
                    )
                )]
            else:
                response.choices = [MagicMock(
                    message=MagicMock(
                        content="Test Segment Title\nA brief summary of the test segment content."
                    )
                )]
            return response
            
        mock_client.chat.completions.create = AsyncMock(side_effect=mock_create_completion)
        
        mock.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
class TestEmbeddingsAndSummaries:
    async def test_generate_embeddings_batch(self, processor, test_segments, mock_openai):
        """Test generating embeddings for multiple segments in batch."""
        await processor._generate_embeddings(test_segments)
        
        # Verify embeddings were generated for all segments
        for segment in test_segments:
            assert segment.embedding is not None
            assert len(segment.embedding) == 1536
            assert isinstance(segment.embedding, list)
            assert all(isinstance(x, float) for x in segment.embedding)
        
        # Verify batch processing
        assert mock_openai.embeddings.create.call_count == 1  # Should process all segments in one batch

    async def test_generate_embeddings_error_handling(self, processor, test_segments, mock_openai):
        """Test error handling during embedding generation."""
        # Simulate API error
        mock_openai.embeddings.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await processor._generate_embeddings(test_segments)
            
        # Verify no embeddings were saved
        for segment in test_segments:
            assert not hasattr(segment, 'embedding')

    async def test_generate_summaries_length_threshold(self, processor, test_segments, mock_openai):
        """Test that summaries are only generated for segments above the length threshold."""
        await processor._generate_summaries(test_segments)
        
        # Short segment should not have summary
        assert not test_segments[0].title
        assert not test_segments[0].display_text
        assert test_segments[0].segment_metadata.get('has_summary') is False
        
        # Long segment should have summary
        assert test_segments[1].title
        assert test_segments[1].display_text
        assert test_segments[1].segment_metadata.get('has_summary') is True
        
        # Verify API was only called for long segments
        assert mock_openai.chat.completions.create.call_count == 1

    async def test_generate_summaries_content_handling(self, processor, test_segments, mock_openai):
        """Test that summaries properly handle different types of content."""
        await processor._generate_summaries(test_segments)
        
        # Technical segment should have appropriate title/summary
        technical_segment = test_segments[2]
        if len(technical_segment.text.split()) > 50:  # Only if it meets length threshold
            assert "Technical" in technical_segment.title
            assert "technical terms" in technical_segment.display_text.lower()

    async def test_summary_error_handling(self, processor, test_segments, mock_openai):
        """Test error handling during summary generation."""
        # Simulate API error
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        # Should not raise exception but log error and continue
        await processor._generate_summaries(test_segments)
        
        # Long segment should have error noted in metadata
        long_segment = test_segments[1]
        assert long_segment.segment_metadata.get('summary_error') is not None

    async def test_embedding_consistency(self, processor, test_segments, mock_openai):
        """Test that embeddings are consistent for identical text."""
        # Create two segments with identical text
        identical_segments = [
            Segment(video_id=1, start_time=0.0, end_time=1.0, text="Test text", speaker_id="A"),
            Segment(video_id=1, start_time=1.0, end_time=2.0, text="Test text", speaker_id="B")
        ]
        
        await processor._generate_embeddings(identical_segments)
        
        # Embeddings should be identical for identical text
        assert identical_segments[0].embedding == identical_segments[1].embedding

    async def test_summary_format(self, processor, test_segments, mock_openai):
        """Test that generated summaries follow the expected format."""
        await processor._generate_summaries(test_segments)
        
        long_segment = test_segments[1]
        if long_segment.title:  # Only if summary was generated
            assert len(long_segment.title.split()) <= 5  # Title should be ≤ 5 words
            assert isinstance(long_segment.display_text, str)
            assert long_segment.display_text.strip()  # Summary should not be empty
            assert long_segment.segment_metadata.get('has_summary') is True

    async def test_embedding_persistence(self, processor, test_segments, mock_openai):
        """Test that embeddings are properly prepared for database storage."""
        await processor._generate_embeddings(test_segments)
        
        with patch('src.api.database.db.client.table') as mock_table:
            mock_insert = MagicMock(execute=AsyncMock())
            mock_table.return_value.insert = MagicMock(return_value=mock_insert)
            
            await processor._save_segments(test_segments)
            
            # Verify embeddings were properly formatted for database
            call_args = mock_table.return_value.insert.call_args[0][0]
            for segment_data in call_args:
                assert 'embedding' in segment_data
                assert isinstance(segment_data['embedding'], list)
                assert len(segment_data['embedding']) == 1536 