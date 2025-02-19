"""Segment model definition."""
from datetime import datetime
from typing import Any, Dict, Optional, List

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from src.db.models.base import BaseModel


class Segment(BaseModel):
    """Segment model."""

    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    speaker_id = Column(String)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text)
    display_text = Column(Text)
    title = Column(Text)
    segment_metadata = Column("metadata", JSONB, nullable=False, server_default='{}')
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    video = relationship("Video", back_populates="segments")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Segment(id={self.id}, video_id={self.video_id}, start={self.start_time}, end={self.end_time})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "speaker_id": self.speaker_id,
            "start_time": float(self.start_time) if self.start_time is not None else None,
            "end_time": float(self.end_time) if self.end_time is not None else None,
            "text": self.text,
            "display_text": self.display_text,
            "title": self.title,
            "metadata": self.segment_metadata or {},
            "embedding": list(self.embedding) if self.embedding is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        } 