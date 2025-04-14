import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import openai
from sqlalchemy.orm import Session
from loguru import logger

from src.db.models import Video, Segment, Summary  # Updated import paths
from src.config import settings
from src.pipeline.types import VideoStatus

class SummaryService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.services.OPENAI_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            openai.api_key = self.api_key
        else:
            logger.warning("Summary service is disabled: OPENAI_API_KEY environment variable is not set")

    def create_summary(
        self,
        video_id: int,
        content: str,
        summary_type: str = "auto",
        metadata: dict = None
    ) -> Summary:
        """Create a new summary."""
        try:
            summary = Summary(
                video_id=video_id,
                content=content,
                summary_type=summary_type,
                metadata=metadata
            )
            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)
            return summary
        except Exception as e:
            logger.error(f"Failed to create summary: {e}")
            self.db.rollback()
            raise

    def get_summary(self, summary_id: int) -> Optional[Summary]:
        """Get a summary by ID."""
        try:
            return self.db.query(Summary).filter(Summary.id == summary_id).first()
        except Exception as e:
            logger.error(f"Failed to get summary {summary_id}: {e}")
            raise

    def list_summaries(self, video_id: int) -> List[Summary]:
        """List all summaries for a video."""
        try:
            return self.db.query(Summary).filter(Summary.video_id == video_id).all()
        except Exception as e:
            logger.error(f"Failed to list summaries for video {video_id}: {e}")
            raise

    def update_summary(self, summary_id: int, **kwargs) -> Optional[Summary]:
        """Update a summary's attributes."""
        try:
            summary = self.get_summary(summary_id)
            if not summary:
                return None
            
            for key, value in kwargs.items():
                setattr(summary, key, value)
            
            self.db.commit()
            self.db.refresh(summary)
            return summary
        except Exception as e:
            logger.error(f"Failed to update summary {summary_id}: {e}")
            self.db.rollback()
            raise

    def delete_summary(self, summary_id: int) -> bool:
        """Delete a summary."""
        try:
            summary = self.get_summary(summary_id)
            if not summary:
                return False
            
            self.db.delete(summary)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete summary {summary_id}: {e}")
            self.db.rollback()
            raise

    async def generate_summary(self, video_id: int) -> Dict[str, Any]:
        """Generate a summary for a video."""
        if not self.enabled:
            logger.warning("Summary generation skipped: OpenAI service is disabled")
            return {
                "id": "1",
                "video_id": str(video_id),
                "content": "Summary unavailable - OpenAI API key not configured",
                "key_points": ["API key not configured"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
        # TODO: Implement actual summary generation with OpenAI
        return {
            "id": "1",
            "video_id": str(video_id),
            "content": "This is a placeholder summary.",
            "key_points": ["Point 1", "Point 2"],
            "created_at": "2024-03-19T00:00:00Z",
            "updated_at": "2024-03-19T00:00:00Z"
        }

    def _format_time(self, seconds: float) -> str:
        """Format seconds into MM:SS format."""
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}" 