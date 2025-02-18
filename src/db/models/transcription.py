"""Transcription model definition."""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.models.base import BaseModel


class Transcription(BaseModel):
    """Transcription model.
    
    Attributes:
        id (int): Primary key
        video_id (int): Foreign key to videos table
        raw_response (JSONB): Raw response from Deepgram API
        processed_data (JSONB): Processed transcription data (optional)
        extra_data (JSONB): Additional metadata about the transcription
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """

    __tablename__ = "transcriptions"

    id = Column(Integer, Sequence('transcriptions_id_seq'), primary_key=True, nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    raw_response = Column(JSONB, nullable=False)
    processed_data = Column(JSONB, nullable=True)
    extra_data = Column(JSONB, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    video = relationship("Video", back_populates="transcription")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Transcription(id={self.id}, video_id={self.video_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "raw_response": self.raw_response,
            "processed_data": self.processed_data,
            "extra_data": self.extra_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 