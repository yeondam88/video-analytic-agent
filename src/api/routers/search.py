from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from loguru import logger

from src.api.database import get_db
from src.api.services.embedding_service import EmbeddingService
from src.db.models import Video

router = APIRouter()

class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    video_id: int
    text: str
    start_time: float
    end_time: float
    similarity: float

class SearchRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    query: str
    limit: int = 5
    threshold: float = 0.7

@router.post("/segments", response_model=List[SearchResult])
async def search_segments(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search for video segments using semantic similarity."""
    try:
        service = EmbeddingService(db)
        results = await service.search_similar_segments(
            query=request.query,
            limit=request.limit,
            threshold=request.threshold
        )
        return [SearchResult(**result) for result in results]
    except Exception as e:
        logger.error(f"Failed to search segments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search segments: {str(e)}"
        )

@router.get("/semantic", response_model=List[Dict[str, Any]])
async def semantic_search(
    query: str = Query(..., description="The search query text"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of results to return"),
    threshold: float = Query(default=0.7, ge=0, le=1, description="Minimum similarity threshold"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search for video segments using semantic similarity.
    
    Returns a list of segments ordered by similarity to the query text.
    Each segment includes:
    - id: The segment ID
    - video_id: The video ID
    - text: The segment text
    - start_time: Start time in seconds
    - end_time: End time in seconds
    - speaker_id: Speaker identifier
    - similarity: Similarity score (0-1)
    """
    try:
        embedding_service = EmbeddingService(db)
        results = await embedding_service.search_similar_segments(
            query=query,
            limit=limit,
            threshold=threshold
        )
        return results
    except Exception as e:
        logger.error(f"Failed to perform semantic search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform semantic search: {str(e)}"
        )

@router.get("/segments/{video_id}", response_model=List[Dict[str, Any]])
async def search_video_segments(
    video_id: int,
    query: str = Query(..., description="The search query text"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of results to return"),
    threshold: float = Query(default=0.7, ge=0, le=1, description="Minimum similarity threshold"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search for segments within a specific video using semantic similarity.
    
    Similar to semantic_search but limited to segments from a specific video.
    """
    try:
        # First verify the video exists
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
            
        embedding_service = EmbeddingService(db)
        results = await embedding_service.search_similar_segments(
            query=query,
            limit=limit,
            threshold=threshold
        )
        
        # Filter results for the specific video
        video_results = [r for r in results if r["video_id"] == video_id]
        return video_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search video segments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search video segments: {str(e)}"
        )

@router.get("/videos", response_model=List[Dict[str, Any]])
async def search_videos(
    query: str = Query(..., description="Search query for videos"),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search for videos by title and description."""
    try:
        videos = (
            db.query(Video)
            .filter(
                (Video.title.ilike(f"%{query}%")) |
                (Video.description.ilike(f"%{query}%"))
            )
            .limit(limit)
            .all()
        )
        return [video.to_dict() for video in videos]
    except Exception as e:
        logger.error(f"Failed to search videos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search videos: {str(e)}"
        ) 