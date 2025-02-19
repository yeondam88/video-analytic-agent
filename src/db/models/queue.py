from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from enum import Enum

from src.db.models.base import Base

class QueueStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class QueueItem(Base):
    """Model for queue items."""
    __tablename__ = "queue_items"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False, default=QueueStatus.PENDING)
    priority = Column(Integer, nullable=False, default=0)
    error = Column(String, nullable=True)
    queue_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=True)
    
    # Add check constraint for status values
    __table_args__ = (
        CheckConstraint(
            status.in_([s.value for s in QueueStatus]),
            name='queue_status_check'
        ),
    )
    
    # Relationships
    video = relationship("Video", back_populates="queue_item")

    def to_dict(self) -> Dict[str, Any]:
        """Convert queue item to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "priority": self.priority,
            "error": self.error,
            "metadata": self.queue_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "video_id": self.video_id
        } 