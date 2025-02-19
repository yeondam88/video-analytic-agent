from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from loguru import logger

from src.api.database import get_db
from src.api.services.embedding_service import EmbeddingService
from src.db.models import Video
from src.api.services.search_service import SearchService

router = APIRouter(tags=["search"])

class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    video_id: int
    text: str
    start_time: float
    end_time: float
    similarity: float

class SearchFilters(BaseModel):
    source: Optional[List[str]] = None
    status: Optional[List[str]] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None
    limit: Optional[int] = 20

class SearchResponse(BaseModel):
    keyword_matches: List[Dict[str, Any]]
    semantic_matches: List[Dict[str, Any]]

class BasicSearchRequest(BaseModel):
    """Basic search request model."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 20

class BasicSearchResponse(BaseModel):
    """Basic search response model."""
    results: List[Dict[str, Any]]
    count: int
    query: str

@router.post("/basic", response_model=BasicSearchResponse)
def basic_search(
    request: BasicSearchRequest,
    db: Session = Depends(get_db)
) -> BasicSearchResponse:
    """
    Basic search endpoint using Meilisearch only.
    
    Example request:
    ```json
    {
        "query": "your search query",
        "limit": 20,
        "filters": {
            "source": "YOUTUBE",
            "status": "COMPLETED"
        }
    }
    ```
    """
    try:
        search_service = SearchService(db)
        results = search_service.search_videos(
            query=request.query,
            filters=request.filters,
            limit=request.limit or 20
        )
        
        return BasicSearchResponse(
            results=results,
            count=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Failed to perform basic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/videos", response_model=List[Dict[str, Any]])
async def search_videos(
    request: SearchRequest,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Search videos using keyword-based search."""
    try:
        search_service = SearchService(db)
        filters = {}
        
        if request.filters:
            if request.filters.source:
                filters["source"] = request.filters.source
            if request.filters.status:
                filters["status"] = request.filters.status
            if request.filters.created_after:
                filters["created_at > "] = request.filters.created_after
            if request.filters.created_before:
                filters["created_at < "] = request.filters.created_before
        
        results = await search_service.search_videos(
            query=request.query,
            filters=filters,
            limit=request.limit
        )
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/segments", response_model=List[Dict[str, Any]])
async def search_segments(
    request: SearchRequest,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Search video segments using semantic search."""
    try:
        search_service = SearchService(db)
        filters = {}
        
        if request.filters:
            if request.filters.source:
                filters["video.source"] = request.filters.source
            if request.filters.created_after:
                filters["created_at > "] = request.filters.created_after
            if request.filters.created_before:
                filters["created_at < "] = request.filters.created_before
        
        results = await search_service.semantic_segment_search(
            query=request.query,
            filters=filters,
            limit=request.limit
        )
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hybrid", response_model=SearchResponse)
def hybrid_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResponse:
    """Perform hybrid search combining keyword and semantic search."""
    try:
        search_service = SearchService(db)
        filters = {}
        
        if request.filters:
            if request.filters.source:
                filters["source"] = request.filters.source
            if request.filters.status:
                filters["status"] = request.filters.status
            if request.filters.created_after:
                filters["created_at > "] = request.filters.created_after
            if request.filters.created_before:
                filters["created_at < "] = request.filters.created_before
        
        results = search_service.hybrid_search(
            query=request.query,
            filters=filters,
            limit=request.limit
        )
        return SearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Failed to perform hybrid search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex")
async def reindex_all(
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Reindex all videos and segments in Meilisearch."""
    try:
        search_service = SearchService(db)
        await search_service.reindex_all()
        return {"message": "Successfully reindexed all documents"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def search_videos_old(
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