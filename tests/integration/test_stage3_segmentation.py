"""Integration tests for stage 3 (segmentation) of the video processing pipeline."""
import pytest
from pathlib import Path
import asyncio
import json
from loguru import logger

from src.pipeline.stages.stage1_download.downloader import VideoDownloader
from src.pipeline.stages.stage1_download.audio_extractor import AudioExtractor
from src.pipeline.stages.stage2_transcription.transcriber import DeepgramTranscriber
from src.pipeline.stages.stage3_segmentation.processor import SegmentProcessor
from src.pipeline.models import Video, VideoStatus, VideoSource
from src.api.database import db
from src.config import settings

# Test video data
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

@pytest.fixture
def processor():
    """Create a segment processor instance."""
    return SegmentProcessor()

@pytest.mark.asyncio
async def test_stage3_pipeline(test_video, test_storage_path, downloader, audio_extractor, transcriber, processor):
    """Test the complete stage 3 pipeline."""
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
        
        # Step 3: Transcribe audio
        logger.info("Step 3: Transcribing audio...")
        transcription = await transcriber.transcribe(test_video, audio_path)
        assert transcription is not None
        
        # Save transcription to database
        db.supabase.table("transcriptions").insert({
            "video_id": test_video.id,
            "raw_transcript": json.dumps(transcription),
            "extra_data": {}
        }).execute()
        
        # Step 4: Process segments
        logger.info("Step 4: Processing segments...")
        segments = await processor.process_transcript(test_video, {"raw_transcript": json.dumps(transcription)})
        assert segments is not None
        assert len(segments) > 0
        
        # Validate segments
        for segment in segments:
            assert segment.video_id == test_video.id
            assert segment.start_time >= 0
            assert segment.end_time > segment.start_time
            assert segment.text
            assert segment.speaker_id
            assert segment.embedding is not None
            assert len(segment.embedding) == 1536
            
            # Check if long segments have summaries
            if len(segment.text.split()) > 50:
                assert segment.title is not None
                assert segment.display_text is not None
                assert segment.segment_metadata.get("has_summary") is True
            else:
                assert segment.segment_metadata.get("has_summary") is False
        
        # Verify database state
        result = db.supabase.table("segments").select("*").eq("video_id", test_video.id).execute()
        assert len(result.data) == len(segments)
        
        # Verify video status
        result = db.supabase.table("videos").select("status").eq("id", test_video.id).execute()
        assert result.data[0]["status"] == VideoStatus.COMPLETED.value
        
        logger.info("Stage 3 pipeline test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Stage 3 pipeline test failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            if video_path and video_path.exists():
                await downloader.cleanup(str(video_path))
            if audio_path and audio_path.exists():
                await audio_extractor.cleanup(str(audio_path))
            # Clean up database records
            db.supabase.table("segments").delete().eq("video_id", test_video.id).execute()
            db.supabase.table("transcriptions").delete().eq("video_id", test_video.id).execute()
            db.supabase.table("videos").delete().eq("id", test_video.id).execute()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_stage3_pipeline()) 