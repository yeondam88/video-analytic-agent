import os
import sys
from pathlib import Path
import pytest
import asyncio
from typing import Generator
from dotenv import load_dotenv

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Load test environment variables
load_dotenv(".env.test", override=True)

# Set test-specific environment variables
os.environ.update({
    "SUPABASE_URL": "http://localhost:54321",
    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
    "SUPABASE_DB_HOST": "localhost",
    "SUPABASE_DB_PORT": "54322",
    "SUPABASE_DB_USER": "postgres",
    "SUPABASE_DB_PASSWORD": "postgres",
    "SUPABASE_DB_NAME": "postgres",
    "DEEPGRAM_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZWVwZ3JhbS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
})

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_storage_path(tmp_path_factory) -> Path:
    """Create a temporary storage directory for tests."""
    storage_dir = tmp_path_factory.mktemp("storage")
    videos_dir = storage_dir / "videos"
    audio_dir = storage_dir / "audio"
    
    videos_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)
    
    return storage_dir

@pytest.fixture(scope="function")
def cleanup_storage(test_storage_path):
    """Clean up storage directory after each test."""
    yield
    
    # Clean up video files
    for path in (test_storage_path / "videos").glob("*"):
        if path.is_file():
            path.unlink()
            
    # Clean up audio files
    for path in (test_storage_path / "audio").glob("*"):
        if path.is_file():
            path.unlink()

@pytest.fixture(scope="session")
def test_video_url() -> str:
    """Get test video URL."""
    return "https://www.loom.com/share/test-video-id"

@pytest.fixture(scope="session")
def test_video_data() -> dict:
    """Get test video data."""
    return {
        "url": "https://www.loom.com/share/test-video-id",
        "title": "Test Video",
        "source": "LOOM",
        "source_id": "test-video-id",
        "status": "PENDING",
        "to_process": True,
        "progress": 0.0,
        "extra_data": {}
    }

@pytest.fixture(scope="session")
def test_segment_data(test_video_data) -> dict:
    """Get test segment data."""
    return {
        "video_id": 1,
        "start_time": 0.0,
        "end_time": 10.0,
        "transcript": "This is a test segment",
        "summary": "Test summary",
        "embedding": [0.1] * 1536  # Test embedding vector
    }

@pytest.fixture(scope="session")
def test_summary_data() -> dict:
    """Get test summary data."""
    return {
        "video_id": 1,
        "content": "Test summary content",
        "summary_type": "auto",
        "summary_metadata": {"key": "value"}
    }

def pytest_configure(config):
    """Configure pytest."""
    # Set asyncio_mode to "strict"
    config.option.asyncio_mode = "strict"
    
    # Set default fixture loop scope
    config.option.asyncio_default_fixture_loop_scope = "function"

    # Register custom markers
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "api: mark test as API test")
    
    # Set test environment variables if not already set
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("LOG_LEVEL", "DEBUG") 