"""Pipeline types and enums."""
from enum import Enum


class VideoStatus(str, Enum):
    """Video processing status types."""
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    DOWNLOADED = "DOWNLOADED"
    EXTRACTING_AUDIO = "EXTRACTING_AUDIO"
    AUDIO_EXTRACTED = "AUDIO_EXTRACTED"
    TRANSCRIBING = "TRANSCRIBING"
    TRANSCRIBED = "TRANSCRIBED"
    SEGMENTING = "SEGMENTING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VideoSource(str, Enum):
    """Video source types."""
    LOOM = "LOOM"
    YOUTUBE = "YOUTUBE"

    def __str__(self) -> str:
        return self.value 