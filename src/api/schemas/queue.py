from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from src.db.models.queue import QueueStatus

class QueueItemBase(BaseModel):
    """Base schema for queue items."""
    url: str
    priority: int = Field(0, ge=0, le=10)
    queue_metadata: Optional[Dict[str, Any]] = None

class QueueItemCreate(QueueItemBase):
    """Schema for creating a queue item."""
    pass

class QueueItemUpdate(BaseModel):
    """Schema for updating a queue item."""
    status: Optional[QueueStatus] = None
    error: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=10)
    queue_metadata: Optional[Dict[str, Any]] = None

class QueueItemResponse(QueueItemBase):
    """Schema for queue item responses."""
    id: str
    status: QueueStatus
    video_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 