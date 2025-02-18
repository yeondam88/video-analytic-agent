import pytest
from src.pipeline.models import Video, VideoStatus
from src.pipeline.segmentation.processor import SegmentProcessor


@pytest.fixture
def sample_video():
    return Video(
        id=1,
        loom_video_id="test_video_123",
        title="Test Video",
        status=VideoStatus.TRANSCRIBING
    )


@pytest.fixture
def sample_transcript():
    return {
        "results": {
            "utterances": [
                {
                    "speaker": "A",
                    "start": 0.0,
                    "end": 5.0,
                    "text": "Hello, this is speaker A."
                },
                {
                    "speaker": "B",
                    "start": 6.0,
                    "end": 10.0,
                    "text": "Hi speaker A, this is speaker B."
                },
                {
                    "speaker": "A",
                    "start": 11.0,
                    "end": 15.0,
                    "text": "Nice to meet you speaker B."
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_process_transcript(sample_video, sample_transcript):
    processor = SegmentProcessor()
    segments = await processor.process_transcript(sample_video, sample_transcript)
    
    assert len(segments) == 3
    
    # Check first segment
    assert segments[0].speaker_id == "A"
    assert segments[0].start_time == 0.0
    assert segments[0].end_time == 5.0
    assert segments[0].text == "Hello, this is speaker A."
    assert segments[0].title is not None
    assert segments[0].display_text is not None
    assert segments[0].embedding is not None
    
    # Check second segment
    assert segments[1].speaker_id == "B"
    assert segments[1].start_time == 6.0
    assert segments[1].end_time == 10.0
    
    # Check third segment
    assert segments[2].speaker_id == "A"
    assert segments[2].start_time == 11.0
    assert segments[2].end_time == 15.0


@pytest.mark.asyncio
async def test_process_transcript_empty_utterances(sample_video):
    processor = SegmentProcessor()
    empty_transcript = {"results": {"utterances": []}}
    
    segments = await processor.process_transcript(sample_video, empty_transcript)
    assert len(segments) == 0


@pytest.mark.asyncio
async def test_process_transcript_invalid_transcript(sample_video):
    processor = SegmentProcessor()
    invalid_transcript = {"results": {}}
    
    segments = await processor.process_transcript(sample_video, invalid_transcript)
    assert len(segments) == 0 