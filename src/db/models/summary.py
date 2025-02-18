"""Summary model definition."""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.models.base import BaseModel


class Summary(BaseModel):
    """Summary model."""

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    summary_type = Column(String, nullable=False)
    extra_data = Column(JSONB, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    video = relationship("Video", back_populates="summaries")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Summary(id={self.id}, video_id={self.video_id}, type={self.summary_type})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "content": self.content,
            "summary_type": self.summary_type,
            "extra_data": self.extra_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }