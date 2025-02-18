from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

from src.pipeline.types import VideoStatus

class VideoBase(BaseModel):
    """Base video attributes."""
    url: HttpUrl = Field(..., description="URL of the video to process")
    title: Optional[str] = Field(None, description="Video title")
    description: Optional[str] = Field(None, description="Video description")

class VideoCreate(VideoBase):
    """Schema for video creation request."""
    pass

class VideoUpdate(BaseModel):
    """Schema for video update request."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[VideoStatus] = None

class VideoInDB(VideoBase):
    """Schema for video in database."""
    id: str = Field(..., description="Unique video identifier")
    status: VideoStatus
    duration: Optional[float] = Field(None, description="Video duration in seconds")
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

class VideoResponse(VideoInDB):
    """Schema for video response."""
    segments_count: Optional[int] = Field(0, description="Number of segments")
    has_summary: bool = Field(False, description="Whether video has a summary")
    thumbnail_url: Optional[str] = Field(None, description="URL of the video thumbnail")
    processing_progress: Optional[float] = Field(
        None,
        description="Processing progress percentage",
        ge=0,
        le=100
    )

class VideoList(BaseModel):
    """Schema for list of videos response."""
    items: List[VideoResponse]
    total: int
    page: int
    page_size: int

class VideoSearchQuery(BaseModel):
    """Schema for video search request."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    status: Optional[VideoStatus] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")

class VideoSimilarityResponse(BaseModel):
    """Response model for similar videos."""
    id: int
    title: Optional[str] = None
    url: HttpUrl
    thumbnail_url: Optional[HttpUrl] = None
    similarity_score: float
    segment_count: int
    avg_confidence: float 