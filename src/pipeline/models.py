"""Pipeline models."""
from src.db.models import Video as DBVideo, Segment, Summary, Transcription
from src.pipeline.types import VideoSource, VideoStatus
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
from datetime import datetime

__all__ = ["Video", "Segment", "Summary", "Transcription", "VideoSource", "VideoStatus"]

class ProcessingStep(BaseModel):
    """A step in the video processing pipeline."""
    step: str
    timestamp: str
    status: str
    progress: float
    error: Optional[str] = None

class Video(BaseModel):
    """Video model for pipeline processing."""
    id: Optional[int] = None
    url: str
    source: VideoSource
    source_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    status: VideoStatus = VideoStatus.PENDING
    progress: float = 0.0
    error: Optional[str] = None
    steps_completed: List[str] = Field(default_factory=list)
    processing_details: List[ProcessingStep] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    @classmethod
    def validate_lists(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure lists are properly initialized."""
        # Initialize steps_completed if missing or None
        if 'steps_completed' not in values or values['steps_completed'] is None:
            values['steps_completed'] = []
            
        # Initialize processing_details if missing or None
        if 'processing_details' not in values or values['processing_details'] is None:
            values['processing_details'] = []
            
        # Initialize progress if missing or None
        if 'progress' not in values or values['progress'] is None:
            values['progress'] = 0.0
            
        return values

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        arbitrary_types_allowed = True

    @classmethod
    def from_db(cls, db_video: DBVideo) -> "Video":
        """Create a Video instance from a database Video model."""
        data = {
            "id": db_video.id,
            "url": db_video.url,
            "source": db_video.source,
            "source_id": db_video.source_id,
            "title": db_video.title,
            "description": db_video.description,
            "thumbnail_url": db_video.thumbnail_url,
            "duration": db_video.duration,
            "status": db_video.status,
            "progress": db_video.progress or 0.0,
            "error": db_video.error,
            "steps_completed": db_video.steps_completed or [],
            "processing_details": db_video.processing_details or [],
            "created_at": db_video.created_at,
            "updated_at": db_video.updated_at
        }
        return cls(**data)