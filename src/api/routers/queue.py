from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from loguru import logger

from src.api.database import get_db
from src.api.services.queue_service import QueueService
from src.db.models.queue import QueueStatus

router = APIRouter()

class QueueRequest(BaseModel):
    """Request model for adding URLs to queue."""
    urls: List[HttpUrl]
    priority: Optional[int] = 0
    metadata: Optional[dict] = None

class QueueItemResponse(BaseModel):
    """Response model for queue items."""
    id: str
    url: str
    status: QueueStatus
    priority: int
    error: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    video_id: Optional[str] = None

class QueueStatusResponse(BaseModel):
    """Response model for queue status."""
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0
    total: int = 0

@router.post("/", response_model=List[QueueItemResponse])
async def add_to_queue(
    request: QueueRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Add URLs to the processing queue."""
    try:
        service = QueueService(db)
        items = service.add_to_queue(
            urls=[str(url) for url in request.urls],
            priority=request.priority,
            metadata=request.metadata
        )
        
        # Start processing in background
        for item in items:
            background_tasks.add_task(service.process_next)
        
        return [QueueItemResponse(**item.to_dict()) for item in items]
    except Exception as e:
        logger.error(f"Failed to add items to queue: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to queue: {str(e)}"
        )

@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status(db: Session = Depends(get_db)):
    """Get current queue status."""
    try:
        service = QueueService(db)
        status = service.get_queue_status()
        total = sum(status.values())
        
        return QueueStatusResponse(
            pending=status.get(QueueStatus.PENDING, 0),
            processing=status.get(QueueStatus.PROCESSING, 0),
            completed=status.get(QueueStatus.COMPLETED, 0),
            failed=status.get(QueueStatus.FAILED, 0),
            total=total
        )
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue status: {str(e)}"
        )

@router.get("/items", response_model=List[QueueItemResponse])
async def get_queue_items(
    status: Optional[QueueStatus] = None,
    skip: int = 0,
    limit: int = 100,
    include_completed: bool = False,
    db: Session = Depends(get_db)
):
    """Get queue items with optional filtering."""
    try:
        service = QueueService(db)
        items = service.get_items(
            status=status,
            skip=skip,
            limit=limit,
            include_completed=include_completed
        )
        return [QueueItemResponse(**item.to_dict()) for item in items]
    except Exception as e:
        logger.error(f"Failed to get queue items: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue items: {str(e)}"
        )

@router.post("/retry-failed")
async def retry_failed_items(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retry all failed items."""
    try:
        service = QueueService(db)
        count = service.retry_failed()
        
        if count > 0:
            # Start processing in background
            background_tasks.add_task(process_queue, db)
            
        return {"message": f"Retrying {count} failed items"}
    except Exception as e:
        logger.error(f"Failed to retry failed items: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry failed items: {str(e)}"
        )

@router.post("/clear-completed")
async def clear_completed_items(
    days_old: int = 7,
    db: Session = Depends(get_db)
):
    """Clear completed items older than specified days."""
    try:
        service = QueueService(db)
        count = service.clear_completed(days_old=days_old)
        return {"message": f"Cleared {count} completed items"}
    except Exception as e:
        logger.error(f"Failed to clear completed items: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear completed items: {str(e)}"
        )

async def process_queue(db: Session):
    """Process items in the queue."""
    try:
        service = QueueService(db)
        while True:
            item = service.process_next()
            if not item:
                break
    except Exception as e:
        logger.error(f"Error processing queue: {e}") 