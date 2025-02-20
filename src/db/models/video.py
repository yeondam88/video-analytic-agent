"""Video model definition."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Float, Boolean, ARRAY, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.models.base import BaseModel
from src.pipeline.types import VideoSource, VideoStatus


class Video(BaseModel):
    """Video model."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)  # PostgreSQL IDENTITY is handled by the database
    source = Column(SQLEnum(VideoSource), nullable=False, default=VideoSource.LOOM)
    source_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String)
    description = Column(String)
    duration = Column(Integer)
    status = Column(SQLEnum(VideoStatus), nullable=False, default=VideoStatus.PENDING)
    thumbnail_url = Column(String)
    
    # Progress tracking
    progress = Column(Float, nullable=False, default=0.0)
    steps_completed = Column(ARRAY(String), nullable=False, server_default='{}')
    error = Column(String)
    
    # Results
    transcript = Column(JSONB)
    embeddings = Column(JSONB)
    summary = Column(JSONB)
    extra_data = Column(JSONB, nullable=False, server_default='{}')
    
    # Processing details
    processing_details = Column(JSONB, nullable=False, server_default='[]')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    segments = relationship("Segment", back_populates="video", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="video", cascade="all, delete-orphan")
    transcription = relationship("Transcription", back_populates="video", uselist=False, cascade="all, delete-orphan")
    queue_item = relationship("QueueItem", back_populates="video", uselist=False)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Video(id={self.id}, source={self.source}, title={self.title}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        data = {
            "source": self.source.value if self.source else None,
            "source_id": self.source_id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "status": self.status.value if self.status else None,
            "thumbnail_url": self.thumbnail_url,
            "progress": self.progress if self.progress is not None else 0.0,
            "steps_completed": self.steps_completed or [],
            "error": self.error,
            "transcript": self.transcript,
            "embeddings": self.embeddings,
            "summary": self.summary,
            "extra_data": self.extra_data or {},
            "processing_details": self.processing_details or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if self.id is not None:
            data["id"] = str(self.id)
            
        return data