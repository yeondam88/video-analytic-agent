from datetime import datetime, timedelta
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from loguru import logger

from src.db.models.queue import QueueItem, QueueStatus
from src.api.services.video_service import VideoService
from src.pipeline.video_processor import VideoProcessor

class QueueService:
    def __init__(self, db: Session):
        self.db = db
        self.video_service = VideoService(db)
        self.video_processor = VideoProcessor()

    def add_to_queue(self, urls: List[str], priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> List[QueueItem]:
        """Add multiple URLs to the processing queue."""
        queue_items = []
        is_bulk = len(urls) > 1
        
        for url in urls:
            queue_item = QueueItem(
                id=str(uuid.uuid4()),
                url=url,
                status=QueueStatus.PENDING,
                priority=priority,
                queue_metadata={
                    **(metadata or {}),
                    "is_bulk": is_bulk,
                    "bulk_size": len(urls) if is_bulk else 1,
                    "added_at": datetime.utcnow().isoformat()
                }
            )
            self.db.add(queue_item)
            queue_items.append(queue_item)
        
        try:
            self.db.commit()
            logger.info(f"Added {len(urls)} items to queue (bulk={is_bulk})")
            return queue_items
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add items to queue: {e}")
            raise

    def get_next_item(self) -> Optional[QueueItem]:
        """Get the next item to process based on priority and creation time."""
        try:
            # First try to get the next item from an existing bulk operation
            bulk_item = self.db.query(QueueItem)\
                .filter(QueueItem.status == QueueStatus.PENDING)\
                .filter(QueueItem.queue_metadata['is_bulk'].astext == 'true')\
                .order_by(desc(QueueItem.priority), asc(QueueItem.created_at))\
                .first()
            
            if bulk_item:
                return bulk_item
                
            # If no bulk items, get the next single item
            return self.db.query(QueueItem)\
                .filter(QueueItem.status == QueueStatus.PENDING)\
                .filter(QueueItem.queue_metadata['is_bulk'].astext == 'false')\
                .order_by(desc(QueueItem.priority), asc(QueueItem.created_at))\
                .first()
        except Exception as e:
            logger.error(f"Failed to get next queue item: {e}")
            return None

    def process_next(self) -> Optional[QueueItem]:
        """Process the next item in the queue."""
        item = self.get_next_item()
        if not item:
            return None

        try:
            # Update item status
            item.status = QueueStatus.PROCESSING
            item.started_at = datetime.utcnow()
            self.db.commit()

            # Create video entry
            video = self.video_service.create_video(
                url=item.url,
                metadata={
                    "queue_id": item.id,
                    "is_bulk": item.queue_metadata.get("is_bulk", False),
                    "bulk_size": item.queue_metadata.get("bulk_size", 1)
                }
            )
            item.video_id = str(video.id)
            self.db.commit()

            # Start processing
            self.video_processor.process_video(video.id)

            # Update queue item
            item.status = QueueStatus.COMPLETED
            item.completed_at = datetime.utcnow()
            self.db.commit()

            return item

        except Exception as e:
            logger.error(f"Failed to process queue item {item.id}: {e}")
            if item:
                item.status = QueueStatus.FAILED
                item.error = str(e)
                self.db.commit()
            return None

    def get_queue_status(self) -> Dict[str, int]:
        """Get the current status of the queue."""
        try:
            status_counts = {}
            for status in QueueStatus:
                count = self.db.query(QueueItem)\
                    .filter(QueueItem.status == status)\
                    .count()
                status_counts[status] = count
            return status_counts
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {}

    def get_item(self, item_id: str) -> Optional[QueueItem]:
        """Get a specific queue item by ID."""
        try:
            return self.db.query(QueueItem).filter(QueueItem.id == item_id).first()
        except Exception as e:
            logger.error(f"Failed to get queue item {item_id}: {e}")
            return None

    def get_items(self, 
                 status: Optional[QueueStatus] = None,
                 skip: int = 0,
                 limit: int = 100,
                 include_completed: bool = False,
                 is_bulk: Optional[bool] = None) -> List[QueueItem]:
        """Get queue items with optional filtering."""
        try:
            query = self.db.query(QueueItem)
            
            if status:
                query = query.filter(QueueItem.status == status)
            elif not include_completed:
                query = query.filter(QueueItem.status != QueueStatus.COMPLETED)
                
            if is_bulk is not None:
                query = query.filter(QueueItem.queue_metadata['is_bulk'].astext == str(is_bulk).lower())
                
            return query.order_by(desc(QueueItem.priority), desc(QueueItem.created_at))\
                .offset(skip)\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Failed to get queue items: {e}")
            return []

    def retry_failed(self) -> int:
        """Retry all failed items."""
        try:
            count = self.db.query(QueueItem)\
                .filter(QueueItem.status == QueueStatus.FAILED)\
                .update({
                    "status": QueueStatus.PENDING,
                    "error": None,
                    "started_at": None,
                    "completed_at": None
                })
            self.db.commit()
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to retry failed items: {e}")
            return 0

    def clear_completed(self, days_old: int = 7) -> int:
        """Clear completed items older than specified days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            count = self.db.query(QueueItem)\
                .filter(QueueItem.status == QueueStatus.COMPLETED)\
                .filter(QueueItem.completed_at < cutoff)\
                .delete()
            self.db.commit()
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to clear completed items: {e}")
            return 0 