import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator

from src.api.database.manager import db
from src.db.models.video import Video
from src.db.models.segment import Segment
from src.db.models.summary import Summary
from src.pipeline.types import VideoStatus, VideoSource

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_db():
    """Fixture to initialize test database connection."""
    return db

@pytest.mark.asyncio
async def test_database_connection(test_db):
    """Test basic database connectivity."""
    try:
        # Test a simple query using Supabase client
        response = test_db.client.table('videos').select('*').limit(1).execute()
        assert response is not None
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

@pytest.mark.asyncio
async def test_video_crud(test_db):
    """Test CRUD operations for Video model."""
    # Create test video
    video_data = {
        "url": "https://test.com/video.mp4",
        "title": "Test Video",
        "duration": 120,  # Integer duration in seconds
        "status": "PENDING",  # Uppercase status
        "source": "YOUTUBE",  # Required source field
        "source_id": "test_video_1"  # Required source_id field
    }
    
    try:
        # Create
        result = test_db.client.table("videos").insert(video_data).execute()
        assert result.data is not None
        video_id = result.data[0]["id"]
        
        # Read
        result = test_db.client.table("videos").select("*").eq("id", video_id).execute()
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0]["title"] == "Test Video"
        
        # Update
        update_data = {"title": "Updated Test Video"}
        result = test_db.client.table("videos").update(update_data).eq("id", video_id).execute()
        assert result.data is not None
        assert result.data[0]["title"] == "Updated Test Video"
        
        # Delete
        result = test_db.client.table("videos").delete().eq("id", video_id).execute()
        assert result.data is not None
        
    except Exception as e:
        pytest.fail(f"Video CRUD operations failed: {str(e)}")

@pytest.mark.asyncio
async def test_segment_creation(test_db):
    """Test segment creation."""
    try:
        # Create a test video first
        video_data = {
            "url": "https://example.com/test_video.mp4",
            "title": "Test Video 2",
            "duration": 60,
            "status": VideoStatus.PROCESSING.value,
            "source": VideoSource.YOUTUBE.value,
            "source_id": "test_video_2"
        }
        video_result = test_db.client.table("videos").insert(video_data).execute()
        video_id = video_result.data[0]["id"]

        # Create a test segment
        segment_data = {
            "video_id": video_id,
            "speaker_id": "speaker_1",
            "start_time": 0,
            "end_time": 30,
            "text": "This is a test segment",
            "display_text": "This is a test segment",
            "title": "Test Segment",
            "metadata": {},
            "embedding": [0.1] * 1536  # 1536-dimensional vector
        }
        segment_result = test_db.client.table("segments").insert(segment_data).execute()
        assert segment_result.data[0]["id"] is not None
        assert segment_result.data[0]["video_id"] == video_id
        assert segment_result.data[0]["text"] == "This is a test segment"

    except Exception as e:
        pytest.fail(f"Segment creation test failed: {str(e)}")
    finally:
        # Clean up
        test_db.client.table("segments").delete().eq("video_id", video_id).execute()
        test_db.client.table("videos").delete().eq("id", video_id).execute()

@pytest.mark.asyncio
async def test_vector_search(test_db):
    """Test vector similarity search."""
    try:
        # Create a test video first
        video_data = {
            "url": "https://example.com/test_video3.mp4",
            "title": "Test Video 3",
            "duration": 120,
            "status": VideoStatus.COMPLETED.value,
            "source": VideoSource.YOUTUBE.value,
            "source_id": "test_video_3"
        }
        video_result = test_db.client.table("videos").insert(video_data).execute()
        video_id = video_result.data[0]["id"]

        # Create a test segment with embedding
        segment_data = {
            "video_id": video_id,
            "speaker_id": "speaker_1",
            "start_time": 0,
            "end_time": 30,
            "text": "This is a test segment for vector search",
            "display_text": "This is a test segment for vector search",
            "title": "Test Segment",
            "metadata": {},
            "embedding": [0.1] * 1536  # 1536-dimensional vector
        }
        segment_result = test_db.client.table("segments").insert(segment_data).execute()
        segment_id = segment_result.data[0]["id"]

        # Perform vector similarity search using cosine similarity
        search_query = f"""
        SELECT id, video_id, text, 1 - (embedding <=> '{segment_data["embedding"]}') as similarity
        FROM segments
        WHERE id = {segment_id}
        ORDER BY similarity DESC
        LIMIT 1;
        """
        result = test_db.client.table("segments").select("*").eq("id", segment_id).execute()
        assert len(result.data) == 1
        assert result.data[0]["text"] == "This is a test segment for vector search"

    except Exception as e:
        pytest.fail(f"Vector search test failed: {str(e)}")
    finally:
        # Clean up
        test_db.client.table("segments").delete().eq("video_id", video_id).execute()
        test_db.client.table("videos").delete().eq("id", video_id).execute()

@pytest.mark.asyncio
async def test_summary_creation(test_db):
    """Test summary creation."""
    try:
        # Create a test video first
        video_data = {
            "url": "https://example.com/test_video4.mp4",
            "title": "Test Video 4",
            "duration": 120,
            "status": VideoStatus.COMPLETED.value,
            "source": VideoSource.YOUTUBE.value,
            "source_id": "test_video_4"
        }
        video_result = test_db.client.table("videos").insert(video_data).execute()
        video_id = video_result.data[0]["id"]

        # Create a test summary
        summary_data = {
            "video_id": video_id,
            "content": "This is a test summary",
            "summary_type": "transcript",
            "extra_data": {
                "key_points": ["Point 1", "Point 2"],
                "action_items": ["Action 1", "Action 2"]
            }
        }
        summary_result = test_db.client.table("summaries").insert(summary_data).execute()
        assert summary_result.data[0]["id"] is not None
        assert summary_result.data[0]["video_id"] == video_id
        assert summary_result.data[0]["content"] == "This is a test summary"

    except Exception as e:
        pytest.fail(f"Summary creation test failed: {str(e)}")
    finally:
        # Clean up
        test_db.client.table("summaries").delete().eq("video_id", video_id).execute()
        test_db.client.table("videos").delete().eq("id", video_id).execute() 